import os
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import json
import re
from data_manager import DataStorage, DataAnalyzer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

data_storage = DataStorage()
data_analyzer = DataAnalyzer(data_storage)

criteria_data = {
    "المعيار الأول": {
        "name": "إدارة البرنامج وضمان جودته",
        "description": "يجب أن يكون لدى البرنامج قيادة فعالة تقوم بتطبيق الأنظمة والسياسات واللوائح المؤسسية، وتقوم بالتخطيط والتنفيذ والمتابعة وتفعيل نظم الجودة التي تحقق التطوير المستمر لأدائه في إطار من النزاهة والشفافية والعدالة والمناخ التنظيمي الداعم للعمل.",
        "criteria": [
            {
                "id": "1-1-1",
                "text": "تتسق رسالة البرنامج وأهدافه مع رسالة المؤسسة/الكلية وتوجه جميع عملياته وأنشطته",
                "evidence": [
                    "تحليل احصائي لاستطلاعات أراء المعنيين من الطلاب وأعضاء هيئة التدريس حول الرسالة والاهداف",
                    "اتساق رسالة البرنامج مع أهدافه",
                    "تقرير مجلس القسم عن مدى التقارب والترابط بين أهداف البرنامج والكلية والجامعة",
                    "تقرير الخبراء حول مناسبة رسالة وأهداف البرنامج",
                    "قرارات مجلس القسم فيما يتعلق بالموافقة على رسالة وأهداف البرنامج"
                ]
            },
            {
                "id": "1-1-2",
                "text": "يتوفر لدى البرنامج العدد الكافي من الكوادر المؤهلة للقيام بالمهام الأكاديمية والإدارية والمهنية والفنية، ولهم مهام وصلاحيات محددة",
                "evidence": [
                    "إحصائية بعدد أعضاء هيئة التدريس وموظفي البرنامج",
                    "السير الذاتية محدثة لأعضاء هيئة التدريس",
                    "تقديم شرح للمهام الموكلة لمنسوبي البرنامج من أعضاء هيئة تدريس وموظفين",
                    "تكليف اللجان من مجلس القسم ونماذج من جداول أعضاء هيئة التدريس",
                    "قاعدة بيانات أعضاء هيئة التدريس ومن في حكمهم"
                ]
            },
            {
                "id": "1-1-3",
                "text": "يتوفر للبرنامج مناخ تنظيمي وبيئة أكاديمية داعمة",
                "evidence": [
                    "استطلاعات أراء أعضاء هيئة التدريس والموظفين عن المناخ التنظيمي للبرنامج",
                    "الهيكل التنظيمي للكلية",
                    "دليل البرنامج"
                ]
            }
        ]
    },
    "المعيار الثاني": {
        "name": "التعليم والتعلم",
        "description": "يجب أن يكون لدى البرنامج خصائص واضحة ومتطلبات محددة متوافقة مع الإطار الوطني للمؤهلات ومتطلبات سوق العمل، وتدعم الرسالة، وتتواءم مع خصائص الخريجين، وتحقق المخرجات التعليمية المستهدفة من خلال خطط وطرق تدريس وتقويم متنوعة وفعالة.",
        "criteria": [
            {
                "id": "2-1-1",
                "text": "يتوافق البرنامج مع الإطار الوطني للمؤهلات ومع المعايير الأكاديمية والمهنية، ومتطلبات ممارسة المهنة",
                "evidence": [
                    "مصفوفة توافق البرنامج مع الإطار الوطني للمؤهلات",
                    "تقرير المراجعة الخارجية للبرنامج",
                    "تقرير المقارنة المرجعية للبرنامج",
                    "تقارير الاعتماد المهني (إن وجدت)"
                ]
            },
            {
                "id": "2-1-2",
                "text": "تراعي خصائص الخريجين ومخرجات التعلم احتياجات سوق العمل، ويتم تحديثها بصفة دورية",
                "evidence": [
                    "وثيقة خصائص الخريجين ومخرجات التعلم",
                    "محاضر اجتماعات مراجعة وتحديث خصائص الخريجين ومخرجات التعلم",
                    "استطلاعات آراء أرباب العمل حول خصائص الخريجين",
                    "تقارير المجالس الاستشارية حول مخرجات التعلم"
                ]
            }
        ]
    },
    "المعيار الثالث": {
        "name": "الطلاب",
        "description": "يجب أن تكون معايير وشروط قبول الطلاب واضحة ومعلنة، وأن يتم تطبيقها بعدالة، وأن تكون المعلومات الخاصة بالبرنامج ومتطلبات إكماله متوفرة، ويتم تقديم خدمات التوجيه والإرشاد المناسبة، مع وجود آلية لمتابعة الخريجين.",
        "criteria": [
            {
                "id": "3-1-1",
                "text": "تطبق معايير وشروط قبول الطلاب بعدالة وشفافية",
                "evidence": [
                    "وثيقة شروط القبول المعلنة",
                    "إحصائيات القبول للسنوات الثلاث الأخيرة",
                    "آلية مراجعة وتحديث شروط القبول",
                    "استطلاعات رأي الطلاب حول عدالة وشفافية إجراءات القبول"
                ]
            },
            {
                "id": "3-1-2",
                "text": "تتوفر للبرنامج المعلومات الأساسية للطلاب (مثل: متطلبات الدراسة، الخدمات، والتكاليف المالية إن وجدت)",
                "evidence": [
                    "دليل الطالب",
                    "الموقع الإلكتروني للبرنامج",
                    "مطويات تعريفية بالبرنامج",
                    "برامج التهيئة للطلاب الجدد"
                ]
            }
        ]
    },
    "المعيار الرابع": {
        "name": "هيئة التدريس",
        "description": "يجب أن يتوفر في البرنامج أعداد كافية من هيئة التدريس المؤهلين ذوي الكفاءة والخبرة اللازمة للقيام بمسؤولياتهم التدريسية والبحثية والإدارية والمهنية والمجتمعية.",
        "criteria": [
            {
                "id": "4-1-1",
                "text": "يتوفر في البرنامج العدد الكافي من هيئة التدريس، بمؤهلات وخبرات مناسبة للقيام بمسؤولياتهم التدريسية والبحثية والإدارية والمهنية والمجتمعية",
                "evidence": [
                    "إحصائية بأعداد هيئة التدريس ومؤهلاتهم وتخصصاتهم",
                    "نسبة أعضاء هيئة التدريس إلى الطلاب",
                    "توزيع العبء التدريسي على أعضاء هيئة التدريس",
                    "السير الذاتية لأعضاء هيئة التدريس"
                ]
            },
            {
                "id": "4-1-2",
                "text": "تطبق آليات مناسبة للتحقق من توفر الكفاءة المهنية والتدريسية لهيئة التدريس",
                "evidence": [
                    "آلية تقييم أداء أعضاء هيئة التدريس",
                    "نماذج من تقييم الطلاب لأعضاء هيئة التدريس",
                    "تقارير زيارات الأقران",
                    "خطط التحسين بناءً على نتائج التقييم"
                ]
            }
        ]
    },
    "المعيار الخامس": {
        "name": "مصادر التعلم والمرافق والتجهيزات",
        "description": "يجب أن تكون مصادر التعلم والمرافق والتجهيزات كافية لتلبية احتياجات البرنامج ومقرراته الدراسية، وتتاح لجميع المستفيدين بتنظيم مناسب، كما يجب أن يشترك هيئة التدريس والطلاب في تحديدها بناءً على الاحتياجات.",
        "criteria": [
            {
                "id": "5-1-1",
                "text": "تطبق سياسات وإجراءات مناسبة لتوفير وإتاحة مصادر التعلم والخدمات اللازمة لدعم تعلم الطلاب",
                "evidence": [
                    "سياسات وإجراءات توفير مصادر التعلم",
                    "قائمة بمصادر التعلم المتاحة للبرنامج",
                    "استطلاعات رأي الطلاب وأعضاء هيئة التدريس حول كفاية مصادر التعلم",
                    "خطط تحسين وتطوير مصادر التعلم"
                ]
            },
            {
                "id": "5-1-2",
                "text": "تتوفر للبرنامج القاعات الدراسية والمعامل والمختبرات والتجهيزات المناسبة لاحتياجاته",
                "evidence": [
                    "قائمة بالقاعات الدراسية والمعامل والمختبرات المخصصة للبرنامج",
                    "تقارير الصيانة الدورية للمرافق والتجهيزات",
                    "خطط تحديث وتطوير المرافق والتجهيزات",
                    "استطلاعات رأي المستفيدين حول جودة المرافق والتجهيزات"
                ]
            }
        ]
    }
}

chat_state = {
    "current_step": "welcome",
    "selected_criterion": None,
    "collected_data": {},
    "current_question_index": 0,
    "evidence_data": {},
    "strengths": [],
    "weaknesses": [],
    "improvements": []
}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    emit('message', {'sender': 'bot', 'text': 'مرحباً بك في نظام تقييم الدراسة الذاتية! أنا هنا لمساعدتك في إعداد تقرير الدراسة الذاتية. الرجاء إخباري بالمحك الذي ترغب في تقييمه.'})

@socketio.on('message')
def handle_message(data):
    user_message = data['message']
    
    if chat_state["current_step"] == "welcome":
        criterion_found = False
        
        criterion_id_pattern = re.compile(r'(\d+-\d+-\d+)')
        match = criterion_id_pattern.search(user_message)
        
        if match:
            criterion_id = match.group(1)

            for criterion_key, criterion_data in criteria_data.items():
                for criterion in criterion_data["criteria"]:
                    if criterion["id"] == criterion_id:
                        start_criterion_analysis(criterion)
                        criterion_found = True
                        break
                if criterion_found:
                    break
        
        if not criterion_found:
            for criterion_key, criterion_data in criteria_data.items():
                for criterion in criterion_data["criteria"]:
                    if criterion["text"] in user_message:
                        start_criterion_analysis(criterion)
                        criterion_found = True
                        break
                if criterion_found:
                    break
        
        if not criterion_found:
            emit('message', {
                'sender': 'bot', 
                'text': 'لم أتمكن من تحديد المحك. الرجاء تحديد رقم المحك (مثل 1-1-1) أو نصه بشكل واضح، أو اختيار محك من القائمة الجانبية.'
            })
    
    elif chat_state["current_step"] == "analyze_criterion":
        current_evidence = chat_state["current_evidence"]
        
        if any(word in user_message.lower() for word in ["نعم", "متوفر", "موجود", "يوجد"]):
            chat_state["evidence_data"][current_evidence] = {
                "available": True,
                "implemented": None
            }
            
            emit('message', {
                'sender': 'bot', 
                'text': f'هل تم تنفيذ المتطلبات المتعلقة بـ: {current_evidence}؟'
            })
            chat_state["current_step"] = "check_implementation"
        else:
            chat_state["evidence_data"][current_evidence] = {
                "available": False,
                "implemented": False
            }
            
            move_to_next_evidence()
    
    elif chat_state["current_step"] == "check_implementation":
        current_evidence = chat_state["current_evidence"]
        
        if any(word in user_message.lower() for word in ["نعم", "تم", "منفذ", "مكتمل"]):
            chat_state["evidence_data"][current_evidence]["implemented"] = True
        else:
            chat_state["evidence_data"][current_evidence]["implemented"] = False
        
        move_to_next_evidence()
    
    elif chat_state["current_step"] == "summarize":
        reset_chat_state()
        
        emit('message', {
            'sender': 'bot', 
            'text': 'شكراً لك! هل ترغب في تقييم محك آخر؟ الرجاء تحديد المحك التالي.'
        })

def start_criterion_analysis(criterion):
    """بدء تحليل المحك"""
    chat_state["selected_criterion"] = criterion
    chat_state["current_step"] = "analyze_criterion"
    chat_state["current_question_index"] = 0
    chat_state["evidence_data"] = {}
    
    emit('message', {
        'sender': 'bot', 
        'text': f'سنقوم بتحليل المحك: **{criterion["id"]} - {criterion["text"]}**\n\nسأطرح عليك بعض الأسئلة حول الأدلة والشواهد المطلوبة لهذا المحك لمساعدتك في تقييمه.'
    })
    
    if len(criterion["evidence"]) > 0:
        evidence = criterion["evidence"][0]
        chat_state["current_evidence"] = evidence
        emit('message', {
            'sender': 'bot', 
            'text': f'هل يتوفر لديك الدليل التالي: **{evidence}**؟'
        })

def move_to_next_evidence():
    criterion = chat_state["selected_criterion"]
    chat_state["current_question_index"] += 1
    
    if chat_state["current_question_index"] < len(criterion["evidence"]):
        next_evidence = criterion["evidence"][chat_state["current_question_index"]]
        chat_state["current_evidence"] = next_evidence
        chat_state["current_step"] = "analyze_criterion"
        emit('message', {
            'sender': 'bot', 
            'text': f'هل يتوفر لديك الدليل التالي: **{next_evidence}**؟'
        })
    else:
        chat_state["current_step"] = "summarize"
        analyze_and_summarize()

def analyze_and_summarize():
    """تحليل البيانات المجمعة وتقديم ملخص"""
    criterion = chat_state["selected_criterion"]
    evidence_data = chat_state["evidence_data"]
    
    criterion_data = {
        "id": criterion["id"],
        "text": criterion["text"],
        "evidence_data": evidence_data
    }
    
    analysis_results = data_analyzer.analyze_criterion(criterion_data)
    
    criterion_data.update(analysis_results)
    
    data_storage.save_criterion_data(criterion["id"], criterion_data)
    
    summary_text = f"**ملخص تقييم المحك {criterion['id']}**\n\n"
    
    summary_text += "**نقاط القوة:**\n"
    if analysis_results["strengths"]:
        for strength in analysis_results["strengths"]:
            summary_text += f"- {strength}\n"
    else:
        summary_text += "- لم يتم تحديد نقاط قوة\n"
    
    summary_text += "\n**نقاط الضعف:**\n"
    if analysis_results["weaknesses"]:
        for weakness in analysis_results["weaknesses"]:
            summary_text += f"- {weakness}\n"
    else:
        summary_text += "- لم يتم تحديد نقاط ضعف\n"
    
    summary_text += "\n**التحسينات المقترحة:**\n"
    if analysis_results["improvements"]:
        for improvement in analysis_results["improvements"]:
            summary_text += f"- {improvement}\n"
    else:
        summary_text += "- لا توجد تحسينات مقترحة\n"
    
    summary_text += f"\n**التقييم المقترح:** {analysis_results['rating']} - {analysis_results['rating_text']}"
    
    summary_text += "\n\n**توصيات إضافية:**\n"
    for recommendation in analysis_results["additional_recommendations"]:
        summary_text += f"- {recommendation}\n"
    
    evidence_stats = analysis_results["evidence_stats"]
    summary_text += f"\n**إحصائيات الأدلة:**\n"
    summary_text += f"- إجمالي الأدلة المطلوبة: {evidence_stats['total']}\n"
    summary_text += f"- الأدلة المتوفرة: {evidence_stats['available']} ({evidence_stats['availability_percentage']}%)\n"
    summary_text += f"- الأدلة المنفذة: {evidence_stats['implemented']} ({evidence_stats['implementation_percentage']}%)\n"
    
    summary_text += "\n**تم حفظ نتائج التقييم في قاعدة البيانات. يمكنك الوصول إلى التقرير الكامل من خلال زر 'تقارير' في الصفحة الرئيسية.**"
    
    socketio.emit('message', {
        'sender': 'bot', 
        'text': summary_text
    })

def reset_chat_state():
    chat_state["current_step"] = "welcome"
    chat_state["selected_criterion"] = None
    chat_state["collected_data"] = {}
    chat_state["current_question_index"] = 0
    chat_state["evidence_data"] = {}
    chat_state["strengths"] = []
    chat_state["weaknesses"] = []
    chat_state["improvements"] = []

@app.route('/api/reports', methods=['GET'])
def get_reports():
    criteria = data_storage.list_saved_criteria()
    return jsonify(criteria)

@app.route('/api/report/<criterion_id>', methods=['GET'])
def get_report(criterion_id):
    criterion_data = data_storage.load_criterion_data(criterion_id)
    if criterion_data:
        return jsonify(criterion_data)
    else:
        return jsonify({"error": "لم يتم العثور على التقرير"}), 404

@app.route('/api/summary', methods=['GET'])
def get_summary():
    summary = data_analyzer.generate_report_summary()
    if summary:
        return jsonify(summary)
    else:
        return jsonify({"error": "لم يتم العثور على بيانات كافية لإنشاء ملخص"}), 404

@app.route('/api/generate_report', methods=['POST'])
def generate_full_report():
    report_name = request.json.get('report_name', 'self_assessment_report')
    report_path, report = data_storage.generate_report(report_name)
    return jsonify({"report_path": report_path, "report": report})

@app.route('/api/criteria', methods=['GET'])
def get_all_criteria():
    return jsonify(criteria_data)

@app.route('/api/criterion/<criterion_id>', methods=['GET'])
def get_criterion(criterion_id):
    for criterion_key, criterion_data in criteria_data.items():
        for criterion in criterion_data["criteria"]:
            if criterion["id"] == criterion_id:
                return jsonify(criterion)
    return jsonify({"error": "لم يتم العثور على المحك"}), 404

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    statistics = data_analyzer.generate_statistics()
    return jsonify(statistics)

@app.route('/api/export_data', methods=['GET'])
def export_data():
    data = data_storage.export_all_data()
    return jsonify(data)

@app.route('/api/import_data', methods=['POST'])
def import_data():
    data = request.json.get('data', {})
    success = data_storage.import_data(data)
    if success:
        return jsonify({"status": "تم استيراد البيانات بنجاح"})
    else:
        return jsonify({"error": "فشل استيراد البيانات"}), 400

@app.route('/api/reset_data', methods=['POST'])
def reset_data():
    confirm = request.json.get('confirm', False)
    if confirm:
        success = data_storage.reset_all_data()
        if success:
            return jsonify({"status": "تم إعادة تعيين البيانات بنجاح"})
        else:
            return jsonify({"error": "فشل إعادة تعيين البيانات"}), 500
    else:
        return jsonify({"error": "يجب تأكيد إعادة تعيين البيانات"}), 400

if __name__ == '__main__':
    os.makedirs('criteria', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
