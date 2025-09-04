"""截圖服務

提供網頁截圖功能，支持全頁截圖、元素截圖和圖片優化。
"""

import asyncio
import base64
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import structlog
from playwright.async_api import Page, ElementHandle
from PIL import Image
import io

logger = structlog.get_logger(__name__)


@dataclass
class ScreenshotOptions:
    """截圖選項"""
    full_page: bool = True
    quality: int = 80  # JPEG質量 (1-100)
    format: str = "jpeg"  # jpeg, png, webp
    width: Optional[int] = None
    height: Optional[int] = None
    clip: Optional[Dict[str, float]] = None  # {x, y, width, height}
    omit_background: bool = False
    timeout: int = 30000  # 超時時間（毫秒）
    
    # 優化選項
    compress: bool = True
    max_file_size_kb: int = 500  # 最大文件大小（KB）
    resize_if_large: bool = True
    max_width: int = 1920
    max_height: int = 1080


@dataclass
class ScreenshotResult:
    """截圖結果"""
    success: bool
    image_data: Optional[bytes] = None
    base64_data: Optional[str] = None
    file_size_bytes: int = 0
    dimensions: Optional[Tuple[int, int]] = None
    format: str = "jpeg"
    compression_ratio: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ScreenshotService:
    """截圖服務
    
    提供高質量的網頁截圖功能，包括全頁截圖、元素截圖和圖片優化。
    """
    
    def __init__(self):
        self.logger = logger.bind(component="screenshot_service")
        
        # 默認截圖選項
        self.default_options = ScreenshotOptions()
        
        # 統計信息
        self._stats = {
            "total_screenshots": 0,
            "successful_screenshots": 0,
            "failed_screenshots": 0,
            "total_bytes_saved": 0,
            "compression_savings_bytes": 0
        }
    
    async def take_screenshot(self, page: Page, 
                            options: Optional[ScreenshotOptions] = None) -> ScreenshotResult:
        """拍攝頁面截圖
        
        Args:
            page: Playwright頁面對象
            options: 截圖選項
            
        Returns:
            ScreenshotResult: 截圖結果
        """
        if options is None:
            options = self.default_options
        
        self._stats["total_screenshots"] += 1
        start_time = asyncio.get_event_loop().time()
        
        try:
            self.logger.debug(
                "開始截圖",
                url=page.url,
                full_page=options.full_page,
                format=options.format,
                quality=options.quality
            )
            
            # 等待頁面穩定
            await self._wait_for_page_stable(page)
            
            # 準備截圖參數
            screenshot_params = await self._prepare_screenshot_params(page, options)
            
            # 執行截圖
            image_data = await page.screenshot(**screenshot_params)
            
            # 處理和優化圖片
            result = await self._process_screenshot(image_data, options)
            
            # 添加元數據
            execution_time = asyncio.get_event_loop().time() - start_time
            result.metadata = {
                "url": page.url,
                "timestamp": datetime.now().isoformat(),
                "execution_time": execution_time,
                "viewport": await page.evaluate("() => ({width: window.innerWidth, height: window.innerHeight})"),
                "page_title": await page.title()
            }
            
            if result.success:
                self._stats["successful_screenshots"] += 1
                self._stats["total_bytes_saved"] += result.file_size_bytes
                
                if result.compression_ratio:
                    original_size = result.file_size_bytes / result.compression_ratio
                    savings = original_size - result.file_size_bytes
                    self._stats["compression_savings_bytes"] += savings
            else:
                self._stats["failed_screenshots"] += 1
            
            self.logger.debug(
                "截圖完成",
                success=result.success,
                file_size_kb=result.file_size_bytes / 1024,
                dimensions=result.dimensions,
                execution_time=execution_time
            )
            
            return result
            
        except Exception as e:
            self._stats["failed_screenshots"] += 1
            
            self.logger.error(
                "截圖失敗",
                url=page.url,
                error=str(e)
            )
            
            return ScreenshotResult(
                success=False,
                error_message=str(e)
            )
    
    async def take_element_screenshot(self, element: ElementHandle,
                                    options: Optional[ScreenshotOptions] = None) -> ScreenshotResult:
        """拍攝元素截圖
        
        Args:
            element: 頁面元素
            options: 截圖選項
            
        Returns:
            ScreenshotResult: 截圖結果
        """
        if options is None:
            options = self.default_options
        
        self._stats["total_screenshots"] += 1
        start_time = asyncio.get_event_loop().time()
        
        try:
            self.logger.debug("開始元素截圖")
            
            # 準備截圖參數
            screenshot_params = {
                "type": options.format,
                "quality": options.quality if options.format == "jpeg" else None,
                "omit_background": options.omit_background,
                "timeout": options.timeout
            }
            
            # 移除None值
            screenshot_params = {k: v for k, v in screenshot_params.items() if v is not None}
            
            # 執行截圖
            image_data = await element.screenshot(**screenshot_params)
            
            # 處理和優化圖片
            result = await self._process_screenshot(image_data, options)
            
            # 添加元數據
            execution_time = asyncio.get_event_loop().time() - start_time
            result.metadata = {
                "type": "element",
                "timestamp": datetime.now().isoformat(),
                "execution_time": execution_time
            }
            
            if result.success:
                self._stats["successful_screenshots"] += 1
                self._stats["total_bytes_saved"] += result.file_size_bytes
            else:
                self._stats["failed_screenshots"] += 1
            
            return result
            
        except Exception as e:
            self._stats["failed_screenshots"] += 1
            
            self.logger.error("元素截圖失敗", error=str(e))
            
            return ScreenshotResult(
                success=False,
                error_message=str(e)
            )
    
    async def take_multiple_screenshots(self, page: Page, 
                                      selectors: List[str],
                                      options: Optional[ScreenshotOptions] = None) -> List[ScreenshotResult]:
        """拍攝多個元素的截圖
        
        Args:
            page: Playwright頁面對象
            selectors: CSS選擇器列表
            options: 截圖選項
            
        Returns:
            List[ScreenshotResult]: 截圖結果列表
        """
        results = []
        
        for selector in selectors:
            try:
                # 查找元素
                element = await page.query_selector(selector)
                if element:
                    # 滾動到元素
                    await element.scroll_into_view_if_needed()
                    await asyncio.sleep(0.5)  # 等待滾動完成
                    
                    # 截圖
                    result = await self.take_element_screenshot(element, options)
                    if result.metadata:
                        result.metadata["selector"] = selector
                    results.append(result)
                else:
                    results.append(ScreenshotResult(
                        success=False,
                        error_message=f"元素未找到: {selector}",
                        metadata={"selector": selector}
                    ))
            except Exception as e:
                results.append(ScreenshotResult(
                    success=False,
                    error_message=str(e),
                    metadata={"selector": selector}
                ))
        
        successful_count = sum(1 for r in results if r.success)
        self.logger.info(
            "多元素截圖完成",
            total_elements=len(selectors),
            successful_screenshots=successful_count
        )
        
        return results
    
    async def _wait_for_page_stable(self, page: Page, timeout: int = 5000):
        """等待頁面穩定
        
        Args:
            page: 頁面對象
            timeout: 超時時間（毫秒）
        """
        try:
            # 等待網絡空閒
            await page.wait_for_load_state("networkidle", timeout=timeout)
            
            # 等待圖片加載
            await page.evaluate("""
                () => {
                    return new Promise((resolve) => {
                        const images = document.querySelectorAll('img');
                        let loadedCount = 0;
                        const totalImages = images.length;
                        
                        if (totalImages === 0) {
                            resolve();
                            return;
                        }
                        
                        const checkComplete = () => {
                            loadedCount++;
                            if (loadedCount === totalImages) {
                                resolve();
                            }
                        };
                        
                        images.forEach(img => {
                            if (img.complete) {
                                checkComplete();
                            } else {
                                img.onload = checkComplete;
                                img.onerror = checkComplete;
                            }
                        });
                        
                        // 超時保護
                        setTimeout(resolve, 3000);
                    });
                }
            """)
            
            # 額外等待時間
            await asyncio.sleep(1)
            
        except Exception as e:
            self.logger.debug("等待頁面穩定超時", error=str(e))
    
    async def _prepare_screenshot_params(self, page: Page, 
                                       options: ScreenshotOptions) -> Dict[str, Any]:
        """準備截圖參數
        
        Args:
            page: 頁面對象
            options: 截圖選項
            
        Returns:
            Dict[str, Any]: 截圖參數
        """
        params = {
            "type": options.format,
            "full_page": options.full_page,
            "omit_background": options.omit_background,
            "timeout": options.timeout
        }
        
        # 添加質量參數（僅適用於JPEG）
        if options.format == "jpeg":
            params["quality"] = options.quality
        
        # 添加裁剪區域
        if options.clip:
            params["clip"] = options.clip
        
        # 設置視窗大小
        if options.width and options.height:
            await page.set_viewport_size({
                "width": options.width,
                "height": options.height
            })
        
        # 移除None值
        params = {k: v for k, v in params.items() if v is not None}
        
        return params
    
    async def _process_screenshot(self, image_data: bytes, 
                                options: ScreenshotOptions) -> ScreenshotResult:
        """處理和優化截圖
        
        Args:
            image_data: 原始圖片數據
            options: 截圖選項
            
        Returns:
            ScreenshotResult: 處理後的截圖結果
        """
        try:
            original_size = len(image_data)
            processed_data = image_data
            compression_ratio = None
            
            # 如果需要壓縮或調整大小
            if options.compress or options.resize_if_large:
                processed_data, compression_ratio = await self._optimize_image(
                    image_data, options
                )
            
            # 獲取圖片尺寸
            dimensions = await self._get_image_dimensions(processed_data)
            
            # 生成base64編碼
            base64_data = base64.b64encode(processed_data).decode('utf-8')
            
            return ScreenshotResult(
                success=True,
                image_data=processed_data,
                base64_data=base64_data,
                file_size_bytes=len(processed_data),
                dimensions=dimensions,
                format=options.format,
                compression_ratio=compression_ratio
            )
            
        except Exception as e:
            self.logger.error("圖片處理失敗", error=str(e))
            return ScreenshotResult(
                success=False,
                error_message=f"圖片處理失敗: {str(e)}"
            )
    
    async def _optimize_image(self, image_data: bytes, 
                            options: ScreenshotOptions) -> Tuple[bytes, float]:
        """優化圖片
        
        Args:
            image_data: 原始圖片數據
            options: 截圖選項
            
        Returns:
            Tuple[bytes, float]: (優化後的圖片數據, 壓縮比)
        """
        try:
            # 打開圖片
            image = Image.open(io.BytesIO(image_data))
            original_size = len(image_data)
            
            # 調整大小（如果需要）
            if options.resize_if_large:
                width, height = image.size
                if width > options.max_width or height > options.max_height:
                    # 計算縮放比例
                    scale_w = options.max_width / width
                    scale_h = options.max_height / height
                    scale = min(scale_w, scale_h)
                    
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    
                    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    self.logger.debug(
                        "圖片已調整大小",
                        original_size=(width, height),
                        new_size=(new_width, new_height),
                        scale=scale
                    )
            
            # 壓縮圖片
            output = io.BytesIO()
            
            if options.format.lower() == "jpeg":
                # JPEG壓縮
                if image.mode in ("RGBA", "LA", "P"):
                    # 轉換為RGB（JPEG不支持透明度）
                    background = Image.new("RGB", image.size, (255, 255, 255))
                    if image.mode == "P":
                        image = image.convert("RGBA")
                    background.paste(image, mask=image.split()[-1] if image.mode == "RGBA" else None)
                    image = background
                
                # 動態調整質量以滿足文件大小要求
                quality = options.quality
                while quality > 10:
                    output.seek(0)
                    output.truncate()
                    image.save(output, format="JPEG", quality=quality, optimize=True)
                    
                    if len(output.getvalue()) <= options.max_file_size_kb * 1024:
                        break
                    
                    quality -= 10
                
            elif options.format.lower() == "png":
                # PNG壓縮
                image.save(output, format="PNG", optimize=True)
                
            elif options.format.lower() == "webp":
                # WebP壓縮
                quality = options.quality
                while quality > 10:
                    output.seek(0)
                    output.truncate()
                    image.save(output, format="WEBP", quality=quality, optimize=True)
                    
                    if len(output.getvalue()) <= options.max_file_size_kb * 1024:
                        break
                    
                    quality -= 10
            
            optimized_data = output.getvalue()
            optimized_size = len(optimized_data)
            compression_ratio = optimized_size / original_size
            
            self.logger.debug(
                "圖片優化完成",
                original_size_kb=original_size / 1024,
                optimized_size_kb=optimized_size / 1024,
                compression_ratio=compression_ratio,
                savings_percent=(1 - compression_ratio) * 100
            )
            
            return optimized_data, compression_ratio
            
        except Exception as e:
            self.logger.warning("圖片優化失敗，使用原始圖片", error=str(e))
            return image_data, 1.0
    
    async def _get_image_dimensions(self, image_data: bytes) -> Tuple[int, int]:
        """獲取圖片尺寸
        
        Args:
            image_data: 圖片數據
            
        Returns:
            Tuple[int, int]: (寬度, 高度)
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            return image.size
        except Exception as e:
            self.logger.warning("獲取圖片尺寸失敗", error=str(e))
            return (0, 0)
    
    def create_optimized_options(self, target_size_kb: int = 300,
                               max_dimensions: Tuple[int, int] = (1600, 1200)) -> ScreenshotOptions:
        """創建優化的截圖選項
        
        Args:
            target_size_kb: 目標文件大小（KB）
            max_dimensions: 最大尺寸 (寬度, 高度)
            
        Returns:
            ScreenshotOptions: 優化的截圖選項
        """
        return ScreenshotOptions(
            full_page=True,
            quality=85,
            format="jpeg",
            compress=True,
            max_file_size_kb=target_size_kb,
            resize_if_large=True,
            max_width=max_dimensions[0],
            max_height=max_dimensions[1],
            omit_background=True
        )
    
    def create_high_quality_options(self) -> ScreenshotOptions:
        """創建高質量截圖選項
        
        Returns:
            ScreenshotOptions: 高質量截圖選項
        """
        return ScreenshotOptions(
            full_page=True,
            quality=95,
            format="png",
            compress=False,
            resize_if_large=False,
            omit_background=False
        )
    
    def create_fast_options(self) -> ScreenshotOptions:
        """創建快速截圖選項
        
        Returns:
            ScreenshotOptions: 快速截圖選項
        """
        return ScreenshotOptions(
            full_page=False,
            quality=70,
            format="jpeg",
            compress=True,
            max_file_size_kb=200,
            resize_if_large=True,
            max_width=1280,
            max_height=720,
            timeout=15000
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取統計信息
        
        Returns:
            Dict[str, Any]: 統計信息
        """
        stats = self._stats.copy()
        
        # 計算成功率
        if stats["total_screenshots"] > 0:
            stats["success_rate"] = (stats["successful_screenshots"] / stats["total_screenshots"]) * 100
        else:
            stats["success_rate"] = 0.0
        
        # 計算平均文件大小
        if stats["successful_screenshots"] > 0:
            stats["average_file_size_kb"] = (stats["total_bytes_saved"] / stats["successful_screenshots"]) / 1024
        else:
            stats["average_file_size_kb"] = 0.0
        
        # 計算壓縮節省
        if stats["compression_savings_bytes"] > 0:
            stats["compression_savings_kb"] = stats["compression_savings_bytes"] / 1024
            stats["compression_savings_percent"] = (stats["compression_savings_bytes"] / 
                                                   (stats["total_bytes_saved"] + stats["compression_savings_bytes"])) * 100
        else:
            stats["compression_savings_kb"] = 0.0
            stats["compression_savings_percent"] = 0.0
        
        return stats