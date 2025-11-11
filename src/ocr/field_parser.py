# src/parsers/field_parser.py
import re
from typing import Dict, Optional, List
from datetime import datetime

class FieldParser:
    def __init__(self):
        """Initialize parser"""
        pass
    
    def parse(self, full_text: str, ocr_results: List) -> Dict[str, Optional[str]]:
        """Parse thông tin - tổng quát cho mọi loại thẻ"""
        # Clean text trước
        text = self._clean_text(full_text)
        
        data = {
            'id_number': self._extract_id_number(text),
            'full_name': self._extract_name(text),
            'date_of_birth': self._extract_dob(text),
            'gender': self._extract_gender(text),
            'nationality': self._extract_nationality(text),
            'place_of_origin': self._extract_origin(text),
            'place_of_residence': self._extract_residence(text),
            'expiry_date': self._extract_expiry(text)
        }
        
        print(f"\n📊 Extracted:")
        for key, value in data.items():
            if value:
                print(f"   ✓ {key}: {value}")
        print()
        
        return data
    
    def _clean_text(self, text: str) -> str:
        """Clean và normalize text"""
        # Gộp các dòng ngắn thành 1 dòng
        text = re.sub(r'\n+', ' ', text)
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        return text
    
    def _extract_id_number(self, text: str) -> Optional[str]:
        """Tìm số ID (12 chữ số)"""
        match = re.search(r'\b\d{12}\b', text)
        return match.group() if match else None
    
    def _extract_name(self, text: str) -> Optional[str]:
        """Tìm họ tên (2-4 từ viết hoa liên tiếp)"""
        # Tìm 2-4 từ viết HOA liên tiếp
        pattern = r'\b([A-ZÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ]{2,}(?:\s+[A-ZÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ]{2,}){1,3})\b'
        
        matches = re.findall(pattern, text)
        
        # Filter: loại bỏ các keyword không phải tên
        blacklist = ['SOCIALIST', 'REPUBLIC', 'VIET', 'NAM', 'CITIZEN', 'IDENTITY', 'CARD', 
                     'INDEPENDENCE', 'FREEDOM', 'HAPPINESS', 'CÔNG', 'DÂN', 'CĂN', 'CƯỚC',
                     'NGHÍA', 'NGHĨA', 'CHỦ', 'CHÙ']
        
        for name in matches:
            # Check không phải keyword
            if not any(kw in name.upper() for kw in blacklist):
                # Check có 2-4 từ
                words = name.split()
                if 2 <= len(words) <= 4:
                    return name
        
        return None
    
    def _extract_dob(self, text: str) -> Optional[str]:
        """Tìm ngày sinh (dd/mm/yyyy) - flexible"""
        # Tìm tất cả dates
        dates = re.findall(r'\b(\d{2}/\d{2}/\d{4})\b', text)
        
        current_year = datetime.now().year
        
        for date in dates:
            try:
                day, month, year = map(int, date.split('/'))
                
                # Validate date hợp lệ
                if not (1 <= day <= 31 and 1 <= month <= 12):
                    continue
                
                # Ngày sinh: từ 1900 đến năm hiện tại
                if 1900 <= year <= current_year:
                    return date
            except:
                continue
        
        return None
    
    def _extract_gender(self, text: str) -> Optional[str]:
        """Tìm giới tính"""
        match = re.search(r'\b(Nam|Nữ|Male|Female)\b', text, re.IGNORECASE)
        if match:
            gender = match.group(1)
            # Capitalize properly
            return gender.capitalize() if gender.lower() in ['nam', 'nữ'] else gender
        return None
    
    def _extract_nationality(self, text: str) -> Optional[str]:
        """Tìm quốc tịch - improved"""
        patterns = [
            r'Nationality[:\s]+([^\n]+)',
            r'(?:Quốc\s*tịch|tich)[:\s]+([^\n]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                line = match.group(1).strip()
                
                # Split bởi các keyword không liên quan
                parts = re.split(r'\s+(?:Giới|Quê|Place|of\s+origin)', line, flags=re.IGNORECASE)
                nationality = parts[0].strip()
                
                # Normalize
                nationality = nationality.replace('Viêt', 'Việt').replace('VIT', 'Việt')
                
                # Validate: chỉ chữ cái và space, 2-20 ký tự
                if re.match(r'^[A-Za-zÀ-ỹ\s]{2,20}$', nationality):
                    return nationality
        
        return None
    
    def _extract_origin(self, text: str) -> Optional[str]:
        """Tìm quê quán"""
        patterns = [
            r'origin[:\s]+(.+?)(?:\s+(?:thuòng|Noi|Place\s+of\s+residence|Có\s+giá)|$)',
            r'Quê\s+quán[:\s/]+(.+?)(?:\s+Nơi|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                origin = match.group(1).strip()
                
                # Remove junk
                origin = re.sub(r'thuòng\s+', '', origin, flags=re.IGNORECASE)
                origin = re.sub(r'\s+', ' ', origin).strip()
                
                # Lấy tối đa 100 ký tự
                if len(origin) > 100:
                    origin = origin[:100] + '...'
                
                if origin and len(origin) > 3:
                    return origin
        
        return None
    
    def _extract_residence(self, text: str) -> Optional[str]:
        """Tìm nơi thường trú - improved"""
        patterns = [
            r'residence[:\s]+(.+?)(?=Có\s+giá|Date\s+of\s+expiry|$)',
            r'Nơi\s+trú[:\s/]+(.+?)(?=Có|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                residence = match.group(1).strip()
                
                # Remove junk text
                junk_patterns = [
                    r'Noi\s+trú[:/\s]+',
                    r'Place\s+of\s+residence[:\s]+',
                    r'thuòng\s+',
                    r'\s+Place\s+\d+.*$',  # "Place 6" and after
                    r'\s+Place$'
                ]
                
                for jp in junk_patterns:
                    residence = re.sub(jp, '', residence, flags=re.IGNORECASE)
                
                # Clean
                residence = re.sub(r'\s+', ' ', residence).strip()
                residence = residence.rstrip('/')
                
                # Validate: phải có ít nhất 1 chữ cái
                if residence and re.search(r'[A-Za-zÀ-ỹ]', residence):
                    # Lấy tối đa 100 ký tự
                    if len(residence) > 100:
                        residence = residence[:100] + '...'
                    return residence
        
        return None
    
    def _extract_expiry(self, text: str) -> Optional[str]:
        """Tìm ngày hết hạn - flexible"""
        patterns = [
            r'(?:Có\s+giá\s+trị\s+đến|giá\s+trj\s+dên)[:\s]+(\d{2}/\d{2}/\d{4})',
            r'(?:Date\s+of\s+)?expiry[:\s]+(\d{2}/\d{2}/\d{4})'
        ]
        
        current_year = datetime.now().year
        
        # Thử tìm theo pattern trước
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date = match.group(1)
                try:
                    year = int(date.split('/')[-1])
                    # Ngày hết hạn: từ năm hiện tại đến +30 năm
                    if current_year <= year <= current_year + 30:
                        return date
                except:
                    continue
        
        # Fallback: tìm date bất kỳ có năm > hiện tại
        dates = re.findall(r'\b(\d{2}/\d{2}/\d{4})\b', text)
        for date in dates:
            try:
                day, month, year = map(int, date.split('/'))
                
                # Validate date
                if not (1 <= day <= 31 and 1 <= month <= 12):
                    continue
                
                # Năm hết hạn phải > năm hiện tại
                if current_year < year <= current_year + 30:
                    return date
            except:
                continue
        
        return None