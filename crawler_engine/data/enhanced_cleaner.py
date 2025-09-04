#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增強數據清理器

提供高級數據清理功能，包括：
- 多語言檢測和處理
- 智能空值填充
- 地理位置標準化
- 數據質量評分
- 重複數據檢測
"""

import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import unicodedata
from collections import Counter


class LanguageCode(Enum):
    """語言代碼枚舉"""
    ENGLISH = "en"
    CHINESE_SIMPLIFIED = "zh-cn"
    CHINESE_TRADITIONAL = "zh-tw"
    ARABIC = "ar"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    JAPANESE = "ja"
    KOREAN = "ko"
    UNKNOWN = "unknown"


class DataQualityLevel(Enum):
    """數據質量等級"""
    EXCELLENT = "excellent"  # 90-100分
    GOOD = "good"           # 70-89分
    FAIR = "fair"           # 50-69分
    POOR = "poor"           # 30-49分
    VERY_POOR = "very_poor" # 0-29分


@dataclass
class CleaningConfig:
    """清理配置"""
    # 語言處理
    detect_language: bool = True
    translate_to_english: bool = False
    preserve_original_language: bool = True
    
    # 空值處理
    fill_empty_values: bool = True
    smart_value_inference: bool = True
    use_ml_prediction: bool = False
    
    # 地理標準化
    standardize_locations: bool = True
    geocode_locations: bool = False
    location_confidence_threshold: float = 0.8
    
    # 數據質量
    calculate_quality_score: bool = True
    quality_threshold: float = 50.0
    
    # 重複檢測
    detect_duplicates: bool = True
    similarity_threshold: float = 0.85
    
    # 文本清理
    remove_html: bool = True
    normalize_unicode: bool = True
    standardize_whitespace: bool = True
    remove_special_chars: bool = False
    
    # 薪資標準化
    standardize_salary: bool = True
    default_currency: str = "AUD"
    salary_range_validation: bool = True


@dataclass
class CleaningResult:
    """清理結果"""
    cleaned_data: Dict[str, Any]
    quality_score: float
    quality_level: DataQualityLevel
    detected_language: LanguageCode
    issues_found: List[str]
    fixes_applied: List[str]
    confidence_scores: Dict[str, float]
    processing_time: float


class EnhancedDataCleaner:
    """增強數據清理器
    
    提供全面的數據清理和標準化功能。
    """
    
    def __init__(self, config: CleaningConfig):
        """初始化增強數據清理器
        
        Args:
            config: 清理配置
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 初始化語言檢測模式
        self._init_language_patterns()
        
        # 初始化地理位置數據
        self._init_location_data()
        
        # 初始化薪資標準化
        self._init_salary_standards()
        
        # 統計信息
        self.stats = {
            'total_processed': 0,
            'languages_detected': Counter(),
            'quality_distribution': Counter(),
            'common_issues': Counter()
        }
    
    def _init_language_patterns(self):
        """初始化語言檢測模式"""
        self.language_patterns = {
            LanguageCode.ENGLISH: {
                'chars': re.compile(r'[a-zA-Z]'),
                'words': ['the', 'and', 'or', 'in', 'at', 'to', 'for', 'of', 'with', 'by'],
                'weight': 1.0
            },
            LanguageCode.CHINESE_SIMPLIFIED: {
                'chars': re.compile(r'[\u4e00-\u9fff]'),
                'words': ['的', '是', '在', '有', '和', '了', '不', '人', '我', '他'],
                'weight': 2.0
            },
            LanguageCode.CHINESE_TRADITIONAL: {
                'chars': re.compile(r'[\u4e00-\u9fff]'),
                'words': ['的', '是', '在', '有', '和', '了', '不', '人', '我', '他'],
                'weight': 2.0
            },
            LanguageCode.ARABIC: {
                'chars': re.compile(r'[\u0600-\u06ff]'),
                'words': ['في', 'من', 'إلى', 'على', 'هذا', 'التي', 'أن', 'كان', 'لا', 'ما'],
                'weight': 2.0
            }
        }
    
    def _init_location_data(self):
        """初始化地理位置標準化數據"""
        # 澳大利亞州/領地標準化
        self.australia_states = {
            'nsw': 'New South Wales',
            'new south wales': 'New South Wales',
            'vic': 'Victoria',
            'victoria': 'Victoria',
            'qld': 'Queensland',
            'queensland': 'Queensland',
            'wa': 'Western Australia',
            'western australia': 'Western Australia',
            'sa': 'South Australia',
            'south australia': 'South Australia',
            'tas': 'Tasmania',
            'tasmania': 'Tasmania',
            'act': 'Australian Capital Territory',
            'australian capital territory': 'Australian Capital Territory',
            'nt': 'Northern Territory',
            'northern territory': 'Northern Territory'
        }
        
        # 主要城市標準化
        self.major_cities = {
            'sydney': {'city': 'Sydney', 'state': 'New South Wales', 'country': 'Australia'},
            'melbourne': {'city': 'Melbourne', 'state': 'Victoria', 'country': 'Australia'},
            'brisbane': {'city': 'Brisbane', 'state': 'Queensland', 'country': 'Australia'},
            'perth': {'city': 'Perth', 'state': 'Western Australia', 'country': 'Australia'},
            'adelaide': {'city': 'Adelaide', 'state': 'South Australia', 'country': 'Australia'},
            'canberra': {'city': 'Canberra', 'state': 'Australian Capital Territory', 'country': 'Australia'},
            'darwin': {'city': 'Darwin', 'state': 'Northern Territory', 'country': 'Australia'},
            'hobart': {'city': 'Hobart', 'state': 'Tasmania', 'country': 'Australia'}
        }
    
    def _init_salary_standards(self):
        """初始化薪資標準化數據"""
        # 貨幣符號映射
        self.currency_symbols = {
            '$': 'AUD',  # 默認澳元
            'A$': 'AUD',
            'AU$': 'AUD',
            'AUD': 'AUD',
            'US$': 'USD',
            'USD': 'USD',
            '€': 'EUR',
            'EUR': 'EUR',
            '£': 'GBP',
            'GBP': 'GBP'
        }
        
        # 薪資範圍驗證（澳元年薪）
        self.salary_ranges = {
            'minimum_wage': 20000,
            'entry_level': (30000, 50000),
            'mid_level': (50000, 80000),
            'senior_level': (80000, 120000),
            'executive_level': (120000, 300000),
            'maximum_reasonable': 500000
        }
    
    def clean_job_data(self, job_data: Dict[str, Any]) -> CleaningResult:
        """清理單個職位數據
        
        Args:
            job_data: 原始職位數據
            
        Returns:
            CleaningResult: 清理結果
        """
        start_time = datetime.now()
        
        cleaned_data = job_data.copy()
        issues_found = []
        fixes_applied = []
        confidence_scores = {}
        
        try:
            # 1. 語言檢測
            detected_language = LanguageCode.UNKNOWN
            if self.config.detect_language:
                detected_language = self._detect_language(cleaned_data)
                confidence_scores['language_detection'] = 0.8  # 簡化的信心分數
            
            # 2. 文本清理
            if self.config.remove_html or self.config.normalize_unicode:
                cleaned_data, text_fixes = self._clean_text_fields(cleaned_data)
                fixes_applied.extend(text_fixes)
            
            # 3. 空值處理
            if self.config.fill_empty_values:
                cleaned_data, empty_fixes = self._handle_empty_values(cleaned_data)
                fixes_applied.extend(empty_fixes)
            
            # 4. 地理位置標準化
            if self.config.standardize_locations:
                cleaned_data, location_fixes = self._standardize_location(cleaned_data)
                fixes_applied.extend(location_fixes)
                confidence_scores['location_standardization'] = 0.9
            
            # 5. 薪資標準化
            if self.config.standardize_salary:
                cleaned_data, salary_fixes = self._standardize_salary(cleaned_data)
                fixes_applied.extend(salary_fixes)
            
            # 6. 數據驗證
            validation_issues = self._validate_data(cleaned_data)
            issues_found.extend(validation_issues)
            
            # 7. 計算質量分數
            quality_score = 0.0
            quality_level = DataQualityLevel.VERY_POOR
            if self.config.calculate_quality_score:
                quality_score = self._calculate_quality_score(cleaned_data, issues_found)
                quality_level = self._get_quality_level(quality_score)
            
            # 更新統計
            self._update_stats(detected_language, quality_level, issues_found)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return CleaningResult(
                cleaned_data=cleaned_data,
                quality_score=quality_score,
                quality_level=quality_level,
                detected_language=detected_language,
                issues_found=issues_found,
                fixes_applied=fixes_applied,
                confidence_scores=confidence_scores,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"數據清理失敗: {e}")
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return CleaningResult(
                cleaned_data=job_data,
                quality_score=0.0,
                quality_level=DataQualityLevel.VERY_POOR,
                detected_language=LanguageCode.UNKNOWN,
                issues_found=[f"清理失敗: {str(e)}"],
                fixes_applied=[],
                confidence_scores={},
                processing_time=processing_time
            )
    
    def _detect_language(self, data: Dict[str, Any]) -> LanguageCode:
        """檢測文本語言
        
        Args:
            data: 數據字典
            
        Returns:
            LanguageCode: 檢測到的語言
        """
        # 合併所有文本字段
        text_fields = ['title', 'description', 'company', 'requirements']
        combined_text = ' '.join([str(data.get(field, '')) for field in text_fields])
        
        if not combined_text.strip():
            return LanguageCode.UNKNOWN
        
        language_scores = {}
        
        for lang, patterns in self.language_patterns.items():
            score = 0.0
            
            # 字符匹配
            char_matches = len(patterns['chars'].findall(combined_text))
            char_ratio = char_matches / len(combined_text) if combined_text else 0
            score += char_ratio * patterns['weight']
            
            # 關鍵詞匹配
            word_matches = sum(1 for word in patterns['words'] if word in combined_text.lower())
            word_ratio = word_matches / len(patterns['words'])
            score += word_ratio * 0.5
            
            language_scores[lang] = score
        
        # 返回得分最高的語言
        if language_scores:
            detected_lang = max(language_scores, key=language_scores.get)
            if language_scores[detected_lang] > 0.1:  # 最低信心閾值
                return detected_lang
        
        return LanguageCode.UNKNOWN
    
    def _clean_text_fields(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """清理文本字段
        
        Args:
            data: 數據字典
            
        Returns:
            Tuple[Dict[str, Any], List[str]]: 清理後的數據和修復記錄
        """
        fixes = []
        text_fields = ['title', 'description', 'company', 'requirements', 'benefits']
        
        for field in text_fields:
            if field in data and data[field]:
                original_value = data[field]
                cleaned_value = original_value
                
                # 移除HTML標籤
                if self.config.remove_html:
                    html_pattern = re.compile(r'<[^>]+>')
                    if html_pattern.search(cleaned_value):
                        cleaned_value = html_pattern.sub('', cleaned_value)
                        fixes.append(f"移除 {field} 中的HTML標籤")
                
                # Unicode標準化
                if self.config.normalize_unicode:
                    normalized = unicodedata.normalize('NFKC', cleaned_value)
                    if normalized != cleaned_value:
                        cleaned_value = normalized
                        fixes.append(f"標準化 {field} 中的Unicode字符")
                
                # 標準化空白字符
                if self.config.standardize_whitespace:
                    whitespace_cleaned = re.sub(r'\s+', ' ', cleaned_value).strip()
                    if whitespace_cleaned != cleaned_value:
                        cleaned_value = whitespace_cleaned
                        fixes.append(f"標準化 {field} 中的空白字符")
                
                # 移除特殊字符（可選）
                if self.config.remove_special_chars:
                    special_chars_removed = re.sub(r'[^\w\s.,!?()-]', '', cleaned_value)
                    if special_chars_removed != cleaned_value:
                        cleaned_value = special_chars_removed
                        fixes.append(f"移除 {field} 中的特殊字符")
                
                data[field] = cleaned_value
        
        return data, fixes
    
    def _handle_empty_values(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """處理空值
        
        Args:
            data: 數據字典
            
        Returns:
            Tuple[Dict[str, Any], List[str]]: 處理後的數據和修復記錄
        """
        fixes = []
        
        # 智能填充規則
        fill_rules = {
            'job_type': 'full-time',
            'salary_currency': self.config.default_currency,
            'salary_type': 'yearly',
            'work_arrangement': 'onsite',
            'experience_level': 'mid-level',
            'posted_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        for field, default_value in fill_rules.items():
            if field in data and (not data[field] or data[field] in ['', 'N/A', 'null', None]):
                data[field] = default_value
                fixes.append(f"填充空值字段 {field} 為 {default_value}")
        
        # 智能推斷
        if self.config.smart_value_inference:
            # 從職位標題推斷經驗等級
            if 'title' in data and data['title']:
                title_lower = data['title'].lower()
                if any(word in title_lower for word in ['senior', 'lead', 'principal', 'architect']):
                    if not data.get('experience_level'):
                        data['experience_level'] = 'senior-level'
                        fixes.append("從職位標題推斷經驗等級為 senior-level")
                elif any(word in title_lower for word in ['junior', 'entry', 'graduate', 'intern']):
                    if not data.get('experience_level'):
                        data['experience_level'] = 'entry-level'
                        fixes.append("從職位標題推斷經驗等級為 entry-level")
            
            # 從描述推斷遠程工作
            if 'description' in data and data['description']:
                desc_lower = data['description'].lower()
                if any(word in desc_lower for word in ['remote', 'work from home', 'wfh', 'telecommute']):
                    if not data.get('work_arrangement'):
                        data['work_arrangement'] = 'remote'
                        fixes.append("從描述推斷工作安排為 remote")
                elif any(word in desc_lower for word in ['hybrid', 'flexible']):
                    if not data.get('work_arrangement'):
                        data['work_arrangement'] = 'hybrid'
                        fixes.append("從描述推斷工作安排為 hybrid")
        
        return data, fixes
    
    def _standardize_location(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """標準化地理位置
        
        Args:
            data: 數據字典
            
        Returns:
            Tuple[Dict[str, Any], List[str]]: 標準化後的數據和修復記錄
        """
        fixes = []
        
        if 'location' in data and data['location']:
            original_location = data['location']
            location_parts = self._parse_location_string(original_location)
            
            # 標準化城市名稱
            if location_parts['city']:
                city_key = location_parts['city'].lower().strip()
                if city_key in self.major_cities:
                    standardized = self.major_cities[city_key]
                    data['city'] = standardized['city']
                    data['state'] = standardized['state']
                    data['country'] = standardized['country']
                    fixes.append(f"標準化城市 {location_parts['city']} 為 {standardized['city']}")
                else:
                    data['city'] = location_parts['city'].title()
            
            # 標準化州/省名稱
            if location_parts['state']:
                state_key = location_parts['state'].lower().strip()
                if state_key in self.australia_states:
                    data['state'] = self.australia_states[state_key]
                    data['country'] = 'Australia'
                    fixes.append(f"標準化州名 {location_parts['state']} 為 {self.australia_states[state_key]}")
                else:
                    data['state'] = location_parts['state'].title()
            
            # 設置默認國家
            if not data.get('country'):
                data['country'] = 'Australia'  # 默認為澳大利亞
                fixes.append("設置默認國家為 Australia")
            
            # 重新構建標準化的位置字符串
            location_parts_list = []
            if data.get('city'):
                location_parts_list.append(data['city'])
            if data.get('state'):
                location_parts_list.append(data['state'])
            if data.get('country') and data['country'] != 'Australia':
                location_parts_list.append(data['country'])
            
            if location_parts_list:
                data['location_standardized'] = ', '.join(location_parts_list)
                if data['location_standardized'] != original_location:
                    fixes.append(f"標準化位置字符串: {original_location} -> {data['location_standardized']}")
        
        return data, fixes
    
    def _parse_location_string(self, location: str) -> Dict[str, str]:
        """解析位置字符串
        
        Args:
            location: 位置字符串
            
        Returns:
            Dict[str, str]: 解析後的位置組件
        """
        if not location:
            return {'city': '', 'state': '', 'country': ''}
        
        # 清理位置字符串
        location = re.sub(r'[^\w\s,.-]', '', location).strip()
        
        # 按逗號分割
        parts = [part.strip() for part in location.split(',') if part.strip()]
        
        result = {'city': '', 'state': '', 'country': ''}
        
        if len(parts) == 1:
            # 只有一個部分，可能是城市或州
            part = parts[0].lower()
            if part in self.major_cities:
                result['city'] = parts[0]
            elif part in self.australia_states:
                result['state'] = parts[0]
            else:
                result['city'] = parts[0]
        elif len(parts) == 2:
            # 兩個部分：城市, 州 或 城市, 國家
            result['city'] = parts[0]
            second_part = parts[1].lower()
            if second_part in self.australia_states:
                result['state'] = parts[1]
            else:
                result['country'] = parts[1]
        elif len(parts) >= 3:
            # 三個或更多部分：城市, 州, 國家
            result['city'] = parts[0]
            result['state'] = parts[1]
            result['country'] = parts[2]
        
        return result
    
    def _standardize_salary(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """標準化薪資信息
        
        Args:
            data: 數據字典
            
        Returns:
            Tuple[Dict[str, Any], List[str]]: 標準化後的數據和修復記錄
        """
        fixes = []
        
        # 處理薪資範圍字符串
        if 'salary_range' in data and data['salary_range']:
            salary_info = self._parse_salary_range(data['salary_range'])
            if salary_info:
                data.update(salary_info)
                fixes.append(f"解析薪資範圍: {data['salary_range']}")
        
        # 驗證和修正薪資值
        salary_fields = ['salary_min', 'salary_max']
        for field in salary_fields:
            if field in data and data[field]:
                try:
                    salary_value = float(data[field])
                    
                    # 檢查合理性
                    if salary_value < self.salary_ranges['minimum_wage']:
                        # 可能是小時工資，轉換為年薪
                        if salary_value > 10:  # 合理的小時工資
                            annual_salary = salary_value * 40 * 52  # 40小時/週 * 52週
                            data[field] = int(annual_salary)
                            fixes.append(f"將 {field} 從小時工資轉換為年薪: {salary_value} -> {annual_salary}")
                    elif salary_value > self.salary_ranges['maximum_reasonable']:
                        self.logger.warning(f"薪資值 {salary_value} 超出合理範圍")
                    
                    # 確保最小值不大於最大值
                    if field == 'salary_max' and 'salary_min' in data:
                        min_val = float(data['salary_min']) if data['salary_min'] else 0
                        if salary_value < min_val:
                            data['salary_min'], data['salary_max'] = data['salary_max'], data['salary_min']
                            fixes.append("交換薪資最小值和最大值")
                    
                except (ValueError, TypeError):
                    self.logger.warning(f"無法解析薪資值: {data[field]}")
        
        # 設置默認貨幣
        if not data.get('salary_currency'):
            data['salary_currency'] = self.config.default_currency
            fixes.append(f"設置默認貨幣為 {self.config.default_currency}")
        
        return data, fixes
    
    def _parse_salary_range(self, salary_range: str) -> Optional[Dict[str, Any]]:
        """解析薪資範圍字符串
        
        Args:
            salary_range: 薪資範圍字符串
            
        Returns:
            Optional[Dict[str, Any]]: 解析後的薪資信息
        """
        if not salary_range:
            return None
        
        # 移除貨幣符號並提取
        currency = 'AUD'  # 默認
        for symbol, curr in self.currency_symbols.items():
            if symbol in salary_range:
                currency = curr
                break
        
        # 提取數字
        numbers = re.findall(r'[\d,]+', salary_range.replace(',', ''))
        if not numbers:
            return None
        
        try:
            if len(numbers) == 1:
                # 單一薪資值
                salary = int(numbers[0])
                return {
                    'salary_min': salary,
                    'salary_max': salary,
                    'salary_currency': currency,
                    'salary_type': 'yearly'
                }
            elif len(numbers) >= 2:
                # 薪資範圍
                min_salary = int(numbers[0])
                max_salary = int(numbers[1])
                
                # 確保順序正確
                if min_salary > max_salary:
                    min_salary, max_salary = max_salary, min_salary
                
                return {
                    'salary_min': min_salary,
                    'salary_max': max_salary,
                    'salary_currency': currency,
                    'salary_type': 'yearly'
                }
        except ValueError:
            return None
        
        return None
    
    def _validate_data(self, data: Dict[str, Any]) -> List[str]:
        """驗證數據質量
        
        Args:
            data: 數據字典
            
        Returns:
            List[str]: 發現的問題列表
        """
        issues = []
        
        # 必需字段檢查
        required_fields = ['title', 'company']
        for field in required_fields:
            if not data.get(field):
                issues.append(f"缺少必需字段: {field}")
        
        # 字段長度檢查
        if data.get('title') and len(data['title']) < 3:
            issues.append("職位標題過短")
        
        if data.get('description') and len(data['description']) < 50:
            issues.append("職位描述過短")
        
        # 薪資合理性檢查
        if data.get('salary_min') and data.get('salary_max'):
            try:
                min_sal = float(data['salary_min'])
                max_sal = float(data['salary_max'])
                
                if min_sal > max_sal:
                    issues.append("最小薪資大於最大薪資")
                
                if min_sal < self.salary_ranges['minimum_wage']:
                    issues.append("薪資低於最低工資標準")
                
                if max_sal > self.salary_ranges['maximum_reasonable']:
                    issues.append("薪資超出合理範圍")
                    
            except (ValueError, TypeError):
                issues.append("薪資格式無效")
        
        # URL格式檢查
        if data.get('url'):
            url_pattern = re.compile(r'https?://[^\s]+')
            if not url_pattern.match(data['url']):
                issues.append("URL格式無效")
        
        return issues
    
    def _calculate_quality_score(self, data: Dict[str, Any], issues: List[str]) -> float:
        """計算數據質量分數
        
        Args:
            data: 數據字典
            issues: 問題列表
            
        Returns:
            float: 質量分數 (0-100)
        """
        score = 100.0
        
        # 扣分項目
        score -= len(issues) * 10  # 每個問題扣10分
        
        # 完整性評分
        important_fields = ['title', 'company', 'location', 'description', 'salary_min', 'salary_max']
        filled_fields = sum(1 for field in important_fields if data.get(field))
        completeness_score = (filled_fields / len(important_fields)) * 30
        
        # 內容質量評分
        content_score = 0
        if data.get('description') and len(data['description']) > 100:
            content_score += 10
        if data.get('title') and len(data['title']) > 5:
            content_score += 5
        if data.get('salary_min') and data.get('salary_max'):
            content_score += 10
        
        final_score = max(0, min(100, score - (100 - completeness_score - content_score)))
        return round(final_score, 2)
    
    def _get_quality_level(self, score: float) -> DataQualityLevel:
        """根據分數獲取質量等級
        
        Args:
            score: 質量分數
            
        Returns:
            DataQualityLevel: 質量等級
        """
        if score >= 90:
            return DataQualityLevel.EXCELLENT
        elif score >= 70:
            return DataQualityLevel.GOOD
        elif score >= 50:
            return DataQualityLevel.FAIR
        elif score >= 30:
            return DataQualityLevel.POOR
        else:
            return DataQualityLevel.VERY_POOR
    
    def _update_stats(self, language: LanguageCode, quality: DataQualityLevel, issues: List[str]):
        """更新統計信息
        
        Args:
            language: 檢測到的語言
            quality: 質量等級
            issues: 問題列表
        """
        self.stats['total_processed'] += 1
        self.stats['languages_detected'][language.value] += 1
        self.stats['quality_distribution'][quality.value] += 1
        
        for issue in issues:
            self.stats['common_issues'][issue] += 1
    
    def get_cleaning_stats(self) -> Dict[str, Any]:
        """獲取清理統計信息
        
        Returns:
            Dict[str, Any]: 統計信息
        """
        return {
            'total_processed': self.stats['total_processed'],
            'languages_detected': dict(self.stats['languages_detected']),
            'quality_distribution': dict(self.stats['quality_distribution']),
            'common_issues': dict(self.stats['common_issues'].most_common(10))
        }


def create_enhanced_cleaner(config: Optional[CleaningConfig] = None) -> EnhancedDataCleaner:
    """創建增強數據清理器的便捷函數
    
    Args:
        config: 清理配置，如果為None則使用默認配置
        
    Returns:
        EnhancedDataCleaner: 增強數據清理器實例
    """
    if config is None:
        config = CleaningConfig()
    
    return EnhancedDataCleaner(config)