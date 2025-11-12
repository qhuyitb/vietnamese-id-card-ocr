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
            'card_type': self.detect_card_type(text),  # ← THÊM NHẬN DIỆN LOẠI THẺ
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
    
    def detect_card_type(self, text: str) -> str:
        """Nhận diện loại giấy tờ"""
        text_upper = text.upper()
        
        if 'CĂN CƯỚC' in text_upper or 'CITIZEN IDENTITY' in text_upper:
            return 'Căn cước công dân'
        elif 'CHỨNG MINH' in text_upper or 'IDENTITY CARD' in text_upper:
            return 'Chứng minh nhân dân'
        elif 'PASSPORT' in text_upper or 'HỘ CHIẾU' in text_upper:
            return 'Hộ chiếu'
        
        return 'Unknown'
    
    def _extract_id_number(self, text: str) -> Optional[str]:
        """Tìm số ID (12 chữ số)"""
        match = re.search(r'\b\d{12}\b', text)
        return match.group() if match else None
    
    def _extract_name(self, text: str) -> Optional[str]:
        """Tìm họ tên - cải thiện với spell correction"""
        # Pattern: 2-4 từ viết HOA liên tiếp
        pattern = r'\b([A-ZÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ]{2,}(?:\s+[A-ZÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ]{2,}){1,3})\b'
        
        matches = re.findall(pattern, text)
        
        # Blacklist mở rộng - thêm các variation không dấu
        blacklist = [
            'SOCIALIST', 'REPUBLIC', 'VIET', 'NAM', 'VIETNAM', 'CITIZEN', 'IDENTITY', 'CARD',
            'INDEPENDENCE', 'FREEDOM', 'HAPPINESS', 'CÔNG', 'CONG', 'HÓA', 'HOA', 'HÒA',
            'DÂN', 'DAN', 'CĂN', 'CAN', 'CƯỚC', 'CUOC', 'CHỦ', 'CHU', 'CHÙ',
            'NGHĨA', 'NGHIA', 'XÃ', 'XA', 'HỘI', 'HOI', 'VIỆT', 'VIET', 'VET'
        ]
        
        valid_names = []
        
        for name in matches:
            # Skip nếu chứa keyword
            if any(kw in name.upper().replace(' ', '') for kw in blacklist):
                continue
            
            # Check có 2-4 từ
            words = name.split()
            if not (2 <= len(words) <= 4):
                continue
            
            # Priority: tên ở giữa text (không phải đầu)
            # Tìm vị trí trong text
            pos = text.find(name)
            score = pos / len(text)  # Càng xa đầu càng tốt
            
            valid_names.append((name, score))
        
        # Sắp xếp theo score, chọn tên ở giữa
        if valid_names:
            valid_names.sort(key=lambda x: x[1], reverse=True)
            name = valid_names[0][0]
            # Fix spelling errors
            name = self._fix_name_spelling(name)
            return name
    
        return None
    
    def _fix_name_spelling(self, name: str) -> str:
        """Fix common OCR errors in Vietnamese names"""
        corrections = {
            'NGUYN': 'NGUYỄN',
            'TRÂN': 'TRẦN',
            'L': 'LÊ',
            'LE': 'LÊ',
            'PHM': 'PHẠM',
            'PHAM': 'PHẠM',
            'HUỲH': 'HUỲNH',
            'HUYNH': 'HUỲNH',
            'VÕ': 'VÕ',
            'VO': 'VÕ',
            'DƯƠNG': 'DƯƠNG',
            'DUONG': 'DƯƠNG',
            'BÙI': 'BÙI',
            'BUI': 'BÙI',
            'ĐÀO': 'ĐÀO',
            'DAO': 'ĐÀO',
            'ĐỖ': 'ĐỖ',
            'DO': 'ĐỖ',
        }
        
        words = name.split()
        fixed_words = []
        
        for word in words:
            # Kiểm tra từng từ có trong corrections không
            fixed_word = corrections.get(word, word)
            fixed_words.append(fixed_word)
        
        return ' '.join(fixed_words)
    
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
        """Tìm giới tính - improved with context"""
        # Ưu tiên tìm theo context trước
        patterns = [
            r'(?:Giới\s*tính|Sex)[:\s]+(Nữ|Nam|Female|Male)',  # Có context
            r'\b(Nữ|Nam|Female|Male)\b'  # Fallback
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                gender = match.group(1)
                # Normalize
                if gender.lower() in ['nữ', 'female']:
                    return 'Nữ'
                elif gender.lower() in ['nam', 'male']:
                    return 'Nam'
        
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
                nationality = nationality.replace('Viêt', 'Việt').replace('VIT', 'Việt').replace('Viet', 'Việt')
                
                # Validate: chỉ chữ cái và space, 2-20 ký tự
                if re.match(r'^[A-Za-zÀ-ỹ\s]{2,20}$', nationality):
                    return nationality
        
        return None
    
    def _extract_origin(self, text: str) -> Optional[str]:
        """Tìm quê quán"""
        patterns = [
            r'origin[:\s]+(.+?)(?:\s+(?:thuòng|thu[oò]ng|Noi|Place\s+of\s+residence|Có\s+giá)|$)',
            r'Quê\s+quán[:\s/]+(.+?)(?:\s+Nơi|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                origin = match.group(1).strip()
                
                # Remove junk
                origin = re.sub(r'thu[oò]ng\s+', '', origin, flags=re.IGNORECASE)
                origin = re.sub(r'\s+', ' ', origin).strip()
                
                # Lấy tối đa 100 ký tự
                if len(origin) > 100:
                    origin = origin[:100] + '...'
                
                if origin and len(origin) > 3:
                    return origin
        
        return None
    
    def _extract_residence(self, text: str) -> Optional[str]:
        """Tìm nơi thường trú - fixed version"""
        patterns = [
            # Pattern 1: Tìm giữa "residence" và "Date of expiry" hoặc "Có giá"
            r'residence[:\s]+(.+?)(?=\s*(?:Co|Có)\s+gia|Date\s+of\s+expiry|$)',
            # Pattern 2: Tiếng Việt
            r'Noi\s+thu[oò]ng\s+tr[uú][:\s/]+(.+?)(?=\s*(?:Co|Có)\s+gia|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                residence = match.group(1).strip()
                
                # Aggressive cleaning - remove junk text
                junk_patterns = [
                    r'Noi\s+trú[:/\s]+',
                    r'Place\s+of\s+residence[:\s]+',
                    r'thu[oò]ng\s+',
                    r'\s*(?:Co|Có)\s+gia.*$',  # Remove "Co gia tri den..."
                    r'\s*Date\s+of.*$',        # Remove "Date of expiry..."
                    r'\s+Place\s+\d+.*$',      # Remove "Place 6"
                    r'\s+Place$',
                ]
                
                for jp in junk_patterns:
                    residence = re.sub(jp, '', residence, flags=re.IGNORECASE)
                
                # Clean spaces and slashes
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
            r'(?:Có\s+giá\s+trị\s+đến|Co\s+gia\s+tri\s+den|giá\s+trj\s+dên)[:\s]+(\d{2}/\d{2}/\d{4})',
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