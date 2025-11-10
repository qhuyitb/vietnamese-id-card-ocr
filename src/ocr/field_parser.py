import re
from typing import Dict, Optional
from datetime import datetime

class FieldParser:
    @staticmethod
    def parse_cccd_front(text: str) -> Dict[str, Optional[str]]:
        """Parse thông tin mặt trước CCCD"""
        data = {
            'id_number': None,
            'full_name': None,
            'date_of_birth': None,
            'gender': None,
            'nationality': None,
            'place_of_origin': None,
            'place_of_residence': None,
            'expiry_date': None
        }
        
        # Số CCCD (12 chữ số)
        id_match = re.search(r'\b\d{12}\b', text)
        if id_match:
            data['id_number'] = id_match.group()
        
        # Họ và tên
        name_match = re.search(r'(?:Họ.*tên|Full.*name)[:\s]+([A-ZÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ\s]+)', text, re.IGNORECASE)
        if name_match:
            data['full_name'] = name_match.group(1).strip()
        
        # Ngày sinh
        dob_match = re.search(r'(?:Ngày.*sinh|Date.*birth)[:\s]+(\d{2}[/-]\d{2}[/-]\d{4})', text, re.IGNORECASE)
        if dob_match:
            data['date_of_birth'] = dob_match.group(1)
        
        # Giới tính
        gender_match = re.search(r'(?:Giới.*tính|Sex)[:\s]+(Nam|Nữ|Male|Female)', text, re.IGNORECASE)
        if gender_match:
            data['gender'] = gender_match.group(1)
        
        # Quốc tịch
        nationality_match = re.search(r'(?:Quốc.*tịch|Nationality)[:\s]+([A-Za-zÀ-ỹ\s]+)', text, re.IGNORECASE)
        if nationality_match:
            data['nationality'] = nationality_match.group(1).strip()
        
        return data
    
    @staticmethod
    def parse_driving_license(text: str) -> Dict[str, Optional[str]]:
        """Parse thông tin bằng lái xe"""
        data = {
            'license_number': None,
            'full_name': None,
            'date_of_birth': None,
            'class': None,
            'issue_date': None,
            'expiry_date': None
        }
        
        # Số bằng lái
        license_match = re.search(r'\b\d{12}\b', text)
        if license_match:
            data['license_number'] = license_match.group()
        
        # Họ và tên
        name_match = re.search(r'(?:Họ.*tên)[:\s]+([A-ZÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ\s]+)', text, re.IGNORECASE)
        if name_match:
            data['full_name'] = name_match.group(1).strip()
        
        # Hạng bằng
        class_match = re.search(r'(?:Hạng)[:\s]+([A-Z0-9, ]+)', text, re.IGNORECASE)
        if class_match:
            data['class'] = class_match.group(1).strip()
        
        return data