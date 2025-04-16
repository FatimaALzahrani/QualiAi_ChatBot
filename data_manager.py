import os
import json
from datetime import datetime

class DataStorage:    
    def __init__(self, storage_dir="data"):
        """تهيئة نظام التخزين"""
        self.storage_dir = storage_dir
        self.ensure_storage_dir_exists()
    
    def ensure_storage_dir_exists(self):
        """التأكد من وجود مجلد التخزين"""
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
            
        criteria_dir = os.path.join(self.storage_dir, "criteria")
        reports_dir = os.path.join(self.storage_dir, "reports")
        
        if not os.path.exists(criteria_dir):
            os.makedirs(criteria_dir)
        
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
    
    def save_criterion_data(self, criterion_id, data):
        """حفظ بيانات المحك"""
        filename = f"{criterion_id.replace('-', '_')}.json"
        filepath = os.path.join(self.storage_dir, "criteria", filename)
        
        data["timestamp"] = datetime.now().isoformat()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        return filepath
    
    def load_criterion_data(self, criterion_id):
        """تحميل بيانات المحك"""
        filename = f"{criterion_id.replace('-', '_')}.json"
        filepath = os.path.join(self.storage_dir, "criteria", filename)
        
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return None
    
    def list_saved_criteria(self):
        """قائمة بالمحكات المحفوظة"""
        criteria_dir = os.path.join(self.storage_dir, "criteria")
        criteria_files = [f for f in os.listdir(criteria_dir) if f.endswith('.json')]
        
        criteria = []
        for file in criteria_files:
            criterion_id = file.replace('_', '-').replace('.json', '')
            filepath = os.path.join(criteria_dir, file)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            criteria.append({
                "id": criterion_id,
                "timestamp": data.get("timestamp", ""),
                "rating": data.get("rating", 0),
                "rating_text": data.get("rating_text", "")
            })
        
        return criteria
    
    def generate_report(self, report_name="self_assessment_report"):
        """إنشاء تقرير شامل"""
        criteria = self.list_saved_criteria()
        
        criteria.sort(key=lambda x: x["id"])
        
        report = {
            "report_name": report_name,
            "generated_at": datetime.now().isoformat(),
            "criteria_count": len(criteria),
            "criteria": [],
            "summary": {
                "ratings": {
                    "1": 0,  # عدم امتثال
                    "2": 0,  # امتثال متدني
                    "3": 0,  # امتثال كبير
                    "4": 0   # امتثال كامل
                },
                "average_rating": 0,
                "strengths_count": 0,
                "weaknesses_count": 0,
                "improvements_count": 0
            }
        }
        
        total_rating = 0
        total_strengths = 0
        total_weaknesses = 0
        total_improvements = 0
        
        for criterion_info in criteria:
            criterion_id = criterion_info["id"]
            criterion_data = self.load_criterion_data(criterion_id)
            
            if criterion_data:
                criterion_report = {
                    "id": criterion_id,
                    "text": criterion_data.get("text", ""),
                    "rating": criterion_data.get("rating", 0),
                    "rating_text": criterion_data.get("rating_text", ""),
                    "strengths": criterion_data.get("strengths", []),
                    "weaknesses": criterion_data.get("weaknesses", []),
                    "improvements": criterion_data.get("improvements", [])
                }
                
                report["criteria"].append(criterion_report)
                
                rating = str(criterion_data.get("rating", 0))
                if rating in report["summary"]["ratings"]:
                    report["summary"]["ratings"][rating] += 1
                
                total_rating += int(criterion_data.get("rating", 0))
                total_strengths += len(criterion_data.get("strengths", []))
                total_weaknesses += len(criterion_data.get("weaknesses", []))
                total_improvements += len(criterion_data.get("improvements", []))
        
        if len(criteria) > 0:
            report["summary"]["average_rating"] = round(total_rating / len(criteria), 2)
        
        report["summary"]["strengths_count"] = total_strengths
        report["summary"]["weaknesses_count"] = total_weaknesses
        report["summary"]["improvements_count"] = total_improvements
        
        report_filename = f"{report_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_filepath = os.path.join(self.storage_dir, "reports", report_filename)
        
        with open(report_filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=4)
        
        return report_filepath, report

class DataAnalyzer:
    """محلل البيانات المجمعة"""
    
    def __init__(self, data_storage):
        """تهيئة محلل البيانات"""
        self.data_storage = data_storage
    
    def analyze_criterion(self, criterion_data):
        """تحليل بيانات المحك"""
        evidence_data = criterion_data.get("evidence_data", {})
        
        strengths = []
        weaknesses = []
        improvements = []
        
        for evidence, data in evidence_data.items():
            if data["available"] and data["implemented"]:
                strengths.append(f"توفر {evidence} وتم تنفيذه بشكل جيد")
            elif data["available"] and not data["implemented"]:
                weaknesses.append(f"توفر {evidence} ولكن لم يتم تنفيذه بشكل كامل")
                improvements.append(f"استكمال تنفيذ {evidence}")
            else:
                weaknesses.append(f"عدم توفر {evidence}")
                improvements.append(f"توفير {evidence}")
        
        total_evidence = len(evidence_data)
        available_count = sum(1 for data in evidence_data.values() if data["available"])
        implemented_count = sum(1 for data in evidence_data.values() if data["implemented"])
        
        if implemented_count == total_evidence:
            rating = 4  # امتثال كامل
            rating_text = "امتثال كامل"
        elif implemented_count >= total_evidence * 0.75:
            rating = 3  # امتثال كبير
            rating_text = "امتثال كبير"
        elif implemented_count >= total_evidence * 0.5:
            rating = 2  # امتثال متدني
            rating_text = "امتثال متدني"
        else:
            rating = 1  # عدم امتثال
            rating_text = "عدم امتثال"
        
        additional_recommendations = []
        if rating <= 2:
            additional_recommendations.append("يوصى بإعداد خطة عمل عاجلة لتحسين هذا المحك")
            additional_recommendations.append("تشكيل فريق عمل مخصص لمتابعة تنفيذ التحسينات")
            additional_recommendations.append("وضع جدول زمني محدد لاستكمال الأدلة والشواهد المطلوبة")
        elif rating == 3:
            additional_recommendations.append("مراجعة وتحسين الأدلة والشواهد غير المكتملة")
            additional_recommendations.append("توثيق الممارسات الجيدة الحالية بشكل أفضل")
        else:
            additional_recommendations.append("الحفاظ على المستوى الحالي من الأداء")
            additional_recommendations.append("مشاركة الممارسات الجيدة مع البرامج الأخرى")
        
        analysis_results = {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "improvements": improvements,
            "rating": rating,
            "rating_text": rating_text,
            "additional_recommendations": additional_recommendations,
            "evidence_stats": {
                "total": total_evidence,
                "available": available_count,
                "implemented": implemented_count,
                "availability_percentage": round(available_count / total_evidence * 100 if total_evidence > 0 else 0, 2),
                "implementation_percentage": round(implemented_count / total_evidence * 100 if total_evidence > 0 else 0, 2)
            }
        }
        
        return analysis_results
    
    def generate_summary(self, criterion_id):
        """إنشاء ملخص للمحك"""
        criterion_data = self.data_storage.load_criterion_data(criterion_id)
        
        if not criterion_data:
            return None
        
        analysis_results = self.analyze_criterion(criterion_data)
        
        criterion_data.update(analysis_results)
        
        self.data_storage.save_criterion_data(criterion_id, criterion_data)
        
        return criterion_data
    
    def generate_report_summary(self):
        """إنشاء ملخص للتقرير الكامل"""
        criteria = self.data_storage.list_saved_criteria()
        
        if not criteria:
            return None
        
        _, report = self.data_storage.generate_report()
        
        summary = report["summary"]
        
        avg_rating = summary["average_rating"]
        if avg_rating >= 3.5:
            overall_level = "ممتاز"
        elif avg_rating >= 2.5:
            overall_level = "جيد"
        elif avg_rating >= 1.5:
            overall_level = "مقبول"
        else:
            overall_level = "ضعيف"
        
        report_summary = {
            "overall_level": overall_level,
            "average_rating": avg_rating,
            "criteria_count": summary["criteria_count"],
            "ratings_distribution": summary["ratings"],
            "strengths_count": summary["strengths_count"],
            "weaknesses_count": summary["weaknesses_count"],
            "improvements_count": summary["improvements_count"],
            "top_criteria": [],
            "bottom_criteria": []
        }
        
        sorted_criteria = sorted(report["criteria"], key=lambda x: x["rating"], reverse=True)
        
        report_summary["top_criteria"] = sorted_criteria[:3] if len(sorted_criteria) >= 3 else sorted_criteria
        
        report_summary["bottom_criteria"] = sorted_criteria[-3:] if len(sorted_criteria) >= 3 else sorted_criteria
        
        return report_summary
