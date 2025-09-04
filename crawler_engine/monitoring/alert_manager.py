"""告警管理器

管理系統告警，支持多種通知渠道和告警規則。
"""

import asyncio
import smtplib
import json
from typing import Dict, List, Optional, Callable, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import structlog
from pathlib import Path

logger = structlog.get_logger(__name__)


class AlertLevel(Enum):
    """告警級別"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertChannel(Enum):
    """告警渠道"""
    EMAIL = "email"
    WEBHOOK = "webhook"
    FILE = "file"
    CONSOLE = "console"
    CUSTOM = "custom"


class AlertStatus(Enum):
    """告警狀態"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    ACKNOWLEDGED = "acknowledged"


@dataclass
class Alert:
    """告警"""
    id: str
    title: str
    message: str
    level: AlertLevel
    source: str  # 告警來源
    timestamp: datetime = field(default_factory=datetime.utcnow)
    status: AlertStatus = AlertStatus.ACTIVE
    metadata: Dict[str, Any] = field(default_factory=dict)
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    suppressed_until: Optional[datetime] = None
    
    @property
    def is_active(self) -> bool:
        """是否為活躍告警"""
        return self.status == AlertStatus.ACTIVE
    
    @property
    def is_resolved(self) -> bool:
        """是否已解決"""
        return self.status == AlertStatus.RESOLVED
    
    @property
    def is_suppressed(self) -> bool:
        """是否被抑制"""
        return (self.status == AlertStatus.SUPPRESSED and 
                self.suppressed_until and 
                datetime.utcnow() < self.suppressed_until)
    
    @property
    def duration(self) -> timedelta:
        """告警持續時間"""
        end_time = self.resolved_at or datetime.utcnow()
        return end_time - self.timestamp
    
    def acknowledge(self, acknowledged_by: str) -> None:
        """確認告警"""
        self.status = AlertStatus.ACKNOWLEDGED
        self.acknowledged_at = datetime.utcnow()
        self.acknowledged_by = acknowledged_by
    
    def resolve(self) -> None:
        """解決告警"""
        self.status = AlertStatus.RESOLVED
        self.resolved_at = datetime.utcnow()
    
    def suppress(self, duration_minutes: int) -> None:
        """抑制告警"""
        self.status = AlertStatus.SUPPRESSED
        self.suppressed_until = datetime.utcnow() + timedelta(minutes=duration_minutes)


@dataclass
class NotificationConfig:
    """通知配置"""
    channel: AlertChannel
    enabled: bool = True
    min_level: AlertLevel = AlertLevel.WARNING
    config: Dict[str, Any] = field(default_factory=dict)
    
    def should_notify(self, alert: Alert) -> bool:
        """是否應該發送通知"""
        if not self.enabled:
            return False
        
        # 檢查告警級別
        level_order = {
            AlertLevel.INFO: 0,
            AlertLevel.WARNING: 1,
            AlertLevel.ERROR: 2,
            AlertLevel.CRITICAL: 3
        }
        
        return level_order[alert.level] >= level_order[self.min_level]


@dataclass
class AlertRule:
    """告警規則"""
    name: str
    condition: Callable[[Dict[str, Any]], bool]
    alert_template: Dict[str, str]
    level: AlertLevel = AlertLevel.WARNING
    cooldown_minutes: int = 60
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not callable(self.condition):
            raise ValueError("condition must be callable")


class NotificationChannel:
    """通知渠道基類"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logger.bind(component=self.__class__.__name__)
    
    async def send_notification(self, alert: Alert) -> bool:
        """發送通知
        
        Args:
            alert: 告警對象
            
        Returns:
            bool: 是否發送成功
        """
        raise NotImplementedError


class EmailNotificationChannel(NotificationChannel):
    """郵件通知渠道"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # 驗證必需的配置
        required_keys = ['smtp_server', 'smtp_port', 'username', 'password', 'to_emails']
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Email notification config missing required key: {key}")
    
    async def send_notification(self, alert: Alert) -> bool:
        """發送郵件通知"""
        try:
            # 創建郵件內容
            msg = MIMEMultipart()
            msg['From'] = self.config['username']
            msg['To'] = ', '.join(self.config['to_emails'])
            msg['Subject'] = f"[{alert.level.value.upper()}] {alert.title}"
            
            # 郵件正文
            body = self._format_email_body(alert)
            msg.attach(MIMEText(body, 'html' if self.config.get('use_html', False) else 'plain'))
            
            # 發送郵件
            with smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port']) as server:
                if self.config.get('use_tls', True):
                    server.starttls()
                
                server.login(self.config['username'], self.config['password'])
                server.send_message(msg)
            
            self.logger.info(
                "郵件通知發送成功",
                alert_id=alert.id,
                to_emails=self.config['to_emails']
            )
            return True
            
        except Exception as e:
            self.logger.error(
                "郵件通知發送失敗",
                alert_id=alert.id,
                error=str(e)
            )
            return False
    
    def _format_email_body(self, alert: Alert) -> str:
        """格式化郵件正文"""
        if self.config.get('use_html', False):
            return f"""
            <html>
            <body>
                <h2>告警通知</h2>
                <table border="1" cellpadding="5" cellspacing="0">
                    <tr><td><strong>告警ID</strong></td><td>{alert.id}</td></tr>
                    <tr><td><strong>標題</strong></td><td>{alert.title}</td></tr>
                    <tr><td><strong>級別</strong></td><td>{alert.level.value.upper()}</td></tr>
                    <tr><td><strong>來源</strong></td><td>{alert.source}</td></tr>
                    <tr><td><strong>時間</strong></td><td>{alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</td></tr>
                    <tr><td><strong>狀態</strong></td><td>{alert.status.value}</td></tr>
                </table>
                <h3>詳細信息</h3>
                <p>{alert.message}</p>
                {self._format_metadata_html(alert.metadata) if alert.metadata else ''}
            </body>
            </html>
            """
        else:
            metadata_str = '\n'.join([f"  {k}: {v}" for k, v in alert.metadata.items()]) if alert.metadata else ''
            return f"""
告警通知

告警ID: {alert.id}
標題: {alert.title}
級別: {alert.level.value.upper()}
來源: {alert.source}
時間: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
狀態: {alert.status.value}

詳細信息:
{alert.message}

{f'元數據:\n{metadata_str}' if metadata_str else ''}
            """
    
    def _format_metadata_html(self, metadata: Dict[str, Any]) -> str:
        """格式化元數據為HTML"""
        if not metadata:
            return ''
        
        rows = ''.join([
            f"<tr><td><strong>{k}</strong></td><td>{v}</td></tr>"
            for k, v in metadata.items()
        ])
        
        return f"""
        <h3>元數據</h3>
        <table border="1" cellpadding="5" cellspacing="0">
            {rows}
        </table>
        """


class WebhookNotificationChannel(NotificationChannel):
    """Webhook通知渠道"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        if 'url' not in config:
            raise ValueError("Webhook notification config missing required key: url")
    
    async def send_notification(self, alert: Alert) -> bool:
        """發送Webhook通知"""
        try:
            import aiohttp
            
            # 準備數據
            payload = {
                'alert_id': alert.id,
                'title': alert.title,
                'message': alert.message,
                'level': alert.level.value,
                'source': alert.source,
                'timestamp': alert.timestamp.isoformat(),
                'status': alert.status.value,
                'metadata': alert.metadata
            }
            
            # 自定義格式化
            if 'format_function' in self.config and callable(self.config['format_function']):
                payload = self.config['format_function'](alert)
            
            # 發送請求
            timeout = aiohttp.ClientTimeout(total=self.config.get('timeout', 30))
            headers = self.config.get('headers', {'Content-Type': 'application/json'})
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.config['url'],
                    json=payload,
                    headers=headers
                ) as response:
                    if 200 <= response.status < 300:
                        self.logger.info(
                            "Webhook通知發送成功",
                            alert_id=alert.id,
                            url=self.config['url'],
                            status_code=response.status
                        )
                        return True
                    else:
                        self.logger.error(
                            "Webhook通知發送失敗",
                            alert_id=alert.id,
                            url=self.config['url'],
                            status_code=response.status
                        )
                        return False
            
        except Exception as e:
            self.logger.error(
                "Webhook通知發送失敗",
                alert_id=alert.id,
                error=str(e)
            )
            return False


class FileNotificationChannel(NotificationChannel):
    """文件通知渠道"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        if 'file_path' not in config:
            raise ValueError("File notification config missing required key: file_path")
        
        # 確保目錄存在
        file_path = Path(config['file_path'])
        file_path.parent.mkdir(parents=True, exist_ok=True)
    
    async def send_notification(self, alert: Alert) -> bool:
        """寫入文件通知"""
        try:
            file_path = Path(self.config['file_path'])
            
            # 準備日誌條目
            log_entry = {
                'timestamp': alert.timestamp.isoformat(),
                'alert_id': alert.id,
                'title': alert.title,
                'message': alert.message,
                'level': alert.level.value,
                'source': alert.source,
                'status': alert.status.value,
                'metadata': alert.metadata
            }
            
            # 寫入文件
            with open(file_path, 'a', encoding='utf-8') as f:
                if self.config.get('format', 'json') == 'json':
                    f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
                else:
                    # 純文本格式
                    f.write(
                        f"[{alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] "
                        f"{alert.level.value.upper()} - {alert.title}: {alert.message}\n"
                    )
            
            self.logger.debug(
                "文件通知寫入成功",
                alert_id=alert.id,
                file_path=str(file_path)
            )
            return True
            
        except Exception as e:
            self.logger.error(
                "文件通知寫入失敗",
                alert_id=alert.id,
                error=str(e)
            )
            return False


class ConsoleNotificationChannel(NotificationChannel):
    """控制台通知渠道"""
    
    async def send_notification(self, alert: Alert) -> bool:
        """控制台輸出通知"""
        try:
            # 根據級別選擇日誌方法
            if alert.level == AlertLevel.CRITICAL:
                log_method = self.logger.critical
            elif alert.level == AlertLevel.ERROR:
                log_method = self.logger.error
            elif alert.level == AlertLevel.WARNING:
                log_method = self.logger.warning
            else:
                log_method = self.logger.info
            
            log_method(
                f"告警通知: {alert.title}",
                alert_id=alert.id,
                message=alert.message,
                source=alert.source,
                level=alert.level.value,
                status=alert.status.value,
                metadata=alert.metadata
            )
            
            return True
            
        except Exception as e:
            self.logger.error(
                "控制台通知輸出失敗",
                alert_id=alert.id,
                error=str(e)
            )
            return False


class CustomNotificationChannel(NotificationChannel):
    """自定義通知渠道"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        if 'send_function' not in config or not callable(config['send_function']):
            raise ValueError("Custom notification config missing required callable: send_function")
    
    async def send_notification(self, alert: Alert) -> bool:
        """自定義通知發送"""
        try:
            send_function = self.config['send_function']
            
            # 執行自定義發送函數
            if asyncio.iscoroutinefunction(send_function):
                result = await send_function(alert)
            else:
                result = send_function(alert)
            
            # 結果應該是布爾值
            success = bool(result)
            
            if success:
                self.logger.info(
                    "自定義通知發送成功",
                    alert_id=alert.id
                )
            else:
                self.logger.error(
                    "自定義通知發送失敗",
                    alert_id=alert.id
                )
            
            return success
            
        except Exception as e:
            self.logger.error(
                "自定義通知發送異常",
                alert_id=alert.id,
                error=str(e)
            )
            return False


class AlertManager:
    """告警管理器
    
    管理告警的創建、通知、確認和解決。
    """
    
    def __init__(self):
        self.logger = logger.bind(component="AlertManager")
        
        # 告警存儲
        self.alerts: Dict[str, Alert] = {}
        
        # 通知配置
        self.notification_configs: List[NotificationConfig] = []
        
        # 通知渠道
        self.notification_channels: Dict[AlertChannel, NotificationChannel] = {}
        
        # 告警規則
        self.alert_rules: Dict[str, AlertRule] = {}
        
        # 告警冷卻
        self.alert_cooldowns: Dict[str, datetime] = {}
        
        # 統計信息
        self.stats = {
            'total_alerts': 0,
            'active_alerts': 0,
            'resolved_alerts': 0,
            'notifications_sent': 0,
            'notifications_failed': 0
        }
        
        # 設置默認控制台通知
        self.add_notification_config(NotificationConfig(
            channel=AlertChannel.CONSOLE,
            enabled=True,
            min_level=AlertLevel.WARNING
        ))
    
    def add_notification_config(self, config: NotificationConfig) -> None:
        """添加通知配置
        
        Args:
            config: 通知配置
        """
        self.notification_configs.append(config)
        
        # 創建對應的通知渠道
        if config.channel not in self.notification_channels:
            if config.channel == AlertChannel.EMAIL:
                self.notification_channels[config.channel] = EmailNotificationChannel(config.config)
            elif config.channel == AlertChannel.WEBHOOK:
                self.notification_channels[config.channel] = WebhookNotificationChannel(config.config)
            elif config.channel == AlertChannel.FILE:
                self.notification_channels[config.channel] = FileNotificationChannel(config.config)
            elif config.channel == AlertChannel.CONSOLE:
                self.notification_channels[config.channel] = ConsoleNotificationChannel(config.config)
            elif config.channel == AlertChannel.CUSTOM:
                self.notification_channels[config.channel] = CustomNotificationChannel(config.config)
        
        self.logger.info(
            "添加通知配置",
            channel=config.channel.value,
            min_level=config.min_level.value,
            enabled=config.enabled
        )
    
    def add_alert_rule(self, rule: AlertRule) -> None:
        """添加告警規則
        
        Args:
            rule: 告警規則
        """
        self.alert_rules[rule.name] = rule
        
        self.logger.info(
            "添加告警規則",
            name=rule.name,
            level=rule.level.value,
            cooldown_minutes=rule.cooldown_minutes,
            enabled=rule.enabled
        )
    
    async def create_alert(self, 
                          title: str,
                          message: str,
                          level: AlertLevel,
                          source: str,
                          alert_id: Optional[str] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> Alert:
        """創建告警
        
        Args:
            title: 告警標題
            message: 告警消息
            level: 告警級別
            source: 告警來源
            alert_id: 告警ID（可選，自動生成）
            metadata: 元數據
            
        Returns:
            Alert: 創建的告警
        """
        if alert_id is None:
            alert_id = f"{source}_{int(datetime.utcnow().timestamp() * 1000)}"
        
        # 檢查是否在冷卻期
        cooldown_key = f"{source}_{title}"
        if cooldown_key in self.alert_cooldowns:
            last_time = self.alert_cooldowns[cooldown_key]
            if (datetime.utcnow() - last_time).total_seconds() < 300:  # 5分鐘冷卻
                self.logger.debug(
                    "告警在冷卻期內，跳過創建",
                    title=title,
                    source=source
                )
                return self.alerts.get(alert_id)  # 返回現有告警或None
        
        # 創建告警
        alert = Alert(
            id=alert_id,
            title=title,
            message=message,
            level=level,
            source=source,
            metadata=metadata or {}
        )
        
        # 存儲告警
        self.alerts[alert_id] = alert
        self.alert_cooldowns[cooldown_key] = datetime.utcnow()
        
        # 更新統計
        self.stats['total_alerts'] += 1
        self.stats['active_alerts'] += 1
        
        self.logger.info(
            "創建告警",
            alert_id=alert_id,
            title=title,
            level=level.value,
            source=source
        )
        
        # 發送通知
        await self._send_notifications(alert)
        
        return alert
    
    async def _send_notifications(self, alert: Alert) -> None:
        """發送通知
        
        Args:
            alert: 告警對象
        """
        if alert.is_suppressed:
            self.logger.debug(
                "告警被抑制，跳過通知",
                alert_id=alert.id
            )
            return
        
        # 並行發送所有通知
        tasks = []
        
        for config in self.notification_configs:
            if config.should_notify(alert):
                channel = self.notification_channels.get(config.channel)
                if channel:
                    task = asyncio.create_task(
                        self._send_single_notification(channel, alert, config.channel)
                    )
                    tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 統計結果
            success_count = sum(1 for result in results if result is True)
            failure_count = len(results) - success_count
            
            self.stats['notifications_sent'] += success_count
            self.stats['notifications_failed'] += failure_count
            
            self.logger.info(
                "通知發送完成",
                alert_id=alert.id,
                success_count=success_count,
                failure_count=failure_count
            )
    
    async def _send_single_notification(self, 
                                       channel: NotificationChannel,
                                       alert: Alert,
                                       channel_type: AlertChannel) -> bool:
        """發送單個通知
        
        Args:
            channel: 通知渠道
            alert: 告警對象
            channel_type: 渠道類型
            
        Returns:
            bool: 是否發送成功
        """
        try:
            return await channel.send_notification(alert)
        except Exception as e:
            self.logger.error(
                "通知發送異常",
                alert_id=alert.id,
                channel=channel_type.value,
                error=str(e)
            )
            return False
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """確認告警
        
        Args:
            alert_id: 告警ID
            acknowledged_by: 確認人
            
        Returns:
            bool: 是否成功
        """
        if alert_id not in self.alerts:
            return False
        
        alert = self.alerts[alert_id]
        alert.acknowledge(acknowledged_by)
        
        self.logger.info(
            "告警已確認",
            alert_id=alert_id,
            acknowledged_by=acknowledged_by
        )
        
        return True
    
    def resolve_alert(self, alert_id: str) -> bool:
        """解決告警
        
        Args:
            alert_id: 告警ID
            
        Returns:
            bool: 是否成功
        """
        if alert_id not in self.alerts:
            return False
        
        alert = self.alerts[alert_id]
        
        if alert.is_active:
            self.stats['active_alerts'] -= 1
            self.stats['resolved_alerts'] += 1
        
        alert.resolve()
        
        self.logger.info(
            "告警已解決",
            alert_id=alert_id,
            duration=str(alert.duration)
        )
        
        return True
    
    def suppress_alert(self, alert_id: str, duration_minutes: int) -> bool:
        """抑制告警
        
        Args:
            alert_id: 告警ID
            duration_minutes: 抑制時長（分鐘）
            
        Returns:
            bool: 是否成功
        """
        if alert_id not in self.alerts:
            return False
        
        alert = self.alerts[alert_id]
        alert.suppress(duration_minutes)
        
        self.logger.info(
            "告警已抑制",
            alert_id=alert_id,
            duration_minutes=duration_minutes
        )
        
        return True
    
    def get_alert(self, alert_id: str) -> Optional[Alert]:
        """獲取告警
        
        Args:
            alert_id: 告警ID
            
        Returns:
            Optional[Alert]: 告警對象
        """
        return self.alerts.get(alert_id)
    
    def get_alerts(self, 
                  status: Optional[AlertStatus] = None,
                  level: Optional[AlertLevel] = None,
                  source: Optional[str] = None,
                  hours: int = 24) -> List[Alert]:
        """獲取告警列表
        
        Args:
            status: 告警狀態過濾
            level: 告警級別過濾
            source: 告警來源過濾
            hours: 時間範圍（小時）
            
        Returns:
            List[Alert]: 告警列表
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        alerts = [
            alert for alert in self.alerts.values()
            if alert.timestamp >= cutoff_time
        ]
        
        if status is not None:
            alerts = [alert for alert in alerts if alert.status == status]
        
        if level is not None:
            alerts = [alert for alert in alerts if alert.level == level]
        
        if source is not None:
            alerts = [alert for alert in alerts if alert.source == source]
        
        return sorted(alerts, key=lambda x: x.timestamp, reverse=True)
    
    def get_active_alerts(self) -> List[Alert]:
        """獲取活躍告警
        
        Returns:
            List[Alert]: 活躍告警列表
        """
        return self.get_alerts(status=AlertStatus.ACTIVE)
    
    def get_critical_alerts(self) -> List[Alert]:
        """獲取關鍵告警
        
        Returns:
            List[Alert]: 關鍵告警列表
        """
        return self.get_alerts(level=AlertLevel.CRITICAL, status=AlertStatus.ACTIVE)
    
    async def evaluate_rules(self, data: Dict[str, Any]) -> List[Alert]:
        """評估告警規則
        
        Args:
            data: 評估數據
            
        Returns:
            List[Alert]: 觸發的告警列表
        """
        triggered_alerts = []
        
        for rule_name, rule in self.alert_rules.items():
            if not rule.enabled:
                continue
            
            # 檢查冷卻期
            if rule_name in self.alert_cooldowns:
                last_time = self.alert_cooldowns[rule_name]
                if (datetime.utcnow() - last_time).total_seconds() < rule.cooldown_minutes * 60:
                    continue
            
            try:
                # 評估條件
                if rule.condition(data):
                    # 創建告警
                    alert = await self.create_alert(
                        title=rule.alert_template.get('title', f'規則觸發: {rule_name}'),
                        message=rule.alert_template.get('message', f'告警規則 {rule_name} 被觸發'),
                        level=rule.level,
                        source=f'rule:{rule_name}',
                        metadata={
                            'rule_name': rule_name,
                            'evaluation_data': data,
                            **rule.metadata
                        }
                    )
                    
                    triggered_alerts.append(alert)
                    self.alert_cooldowns[rule_name] = datetime.utcnow()
                    
                    self.logger.info(
                        "告警規則觸發",
                        rule_name=rule_name,
                        alert_id=alert.id
                    )
                    
            except Exception as e:
                self.logger.error(
                    "告警規則評估失敗",
                    rule_name=rule_name,
                    error=str(e)
                )
        
        return triggered_alerts
    
    def cleanup_old_alerts(self, days: int = 30) -> int:
        """清理舊告警
        
        Args:
            days: 保留天數
            
        Returns:
            int: 清理的告警數量
        """
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        old_alert_ids = [
            alert_id for alert_id, alert in self.alerts.items()
            if alert.timestamp < cutoff_time and alert.is_resolved
        ]
        
        for alert_id in old_alert_ids:
            del self.alerts[alert_id]
        
        # 清理冷卻記錄
        old_cooldown_keys = [
            key for key, timestamp in self.alert_cooldowns.items()
            if timestamp < cutoff_time
        ]
        
        for key in old_cooldown_keys:
            del self.alert_cooldowns[key]
        
        if old_alert_ids:
            self.logger.info(
                "清理舊告警",
                count=len(old_alert_ids),
                days=days
            )
        
        return len(old_alert_ids)
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取統計信息
        
        Returns:
            Dict[str, Any]: 統計信息
        """
        # 更新活躍告警數量
        active_count = len(self.get_active_alerts())
        self.stats['active_alerts'] = active_count
        
        return {
            **self.stats,
            'total_stored_alerts': len(self.alerts),
            'notification_configs': len(self.notification_configs),
            'alert_rules': len(self.alert_rules),
            'notification_channels': len(self.notification_channels)
        }