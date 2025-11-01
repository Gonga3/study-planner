import streamlit as st
import json
import datetime
from datetime import date, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import os

class StudyPlanner:
    def __init__(self):
        st.set_page_config(page_title="برنامه‌ریز درسی", layout="wide")
        
        # داده‌ها
        self.even_week_schedule = {
            "شنبه": [], "یکشنبه": [], "دوشنبه": [],
            "سه‌شنبه": [], "چهارشنبه": [], "پنجشنبه": [], "جمعه": []
        }
        
        self.odd_week_schedule = {
            "شنبه": [], "یکشنبه": [], "دوشنبه": [],
            "سه‌شنبه": [], "چهارشنبه": [], "پنجشنبه": [], "جمعه": []
        }
        
        self.daily_tasks = []
        self.positive_habits = {}
        self.negative_habits = {}
        self.hundred_days = {}
        
        self.load_data()
        self.setup_habits()
        self.setup_hundred_days()
        self.create_app()

    def load_data(self):
        """بارگذاری داده‌های ذخیره شده"""
        try:
            if os.path.exists("study_data.json"):
                with open("study_data.json", 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.even_week_schedule = data.get('even_week_schedule', self.even_week_schedule)
                    self.odd_week_schedule = data.get('odd_week_schedule', self.odd_week_schedule)
                    self.daily_tasks = data.get('daily_tasks', [])
                    self.positive_habits = data.get('positive_habits', {})
                    self.negative_habits = data.get('negative_habits', {})
                    self.hundred_days = data.get('hundred_days', {})
        except Exception as e:
            st.error(f"خطا در بارگذاری داده‌ها: {e}")

    def save_data(self):
        """ذخیره داده‌ها"""
        try:
            data = {
                'even_week_schedule': self.even_week_schedule,
                'odd_week_schedule': self.odd_week_schedule,
                'daily_tasks': self.daily_tasks,
                'positive_habits': self.positive_habits,
                'negative_habits': self.negative_habits,
                'hundred_days': self.hundred_days
            }
            with open("study_data.json", 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            st.error(f"خطا در ذخیره داده‌ها: {e}")

    def setup_habits(self):
        """تنظیم عادت‌های پیش‌فرض"""
        if not self.positive_habits:
            self.positive_habits = {
                'مطالعه روزانه': {'streak': 0, 'history': []},
                'ورزش': {'streak': 0, 'history': []},
                'زبان انگلیسی': {'streak': 0, 'history': []}
            }
        
        if not self.negative_habits:
            self.negative_habits = {
                'دیر خوابیدن': {'days_sober': 0, 'start_date': ''},
                'تعلل در کارها': {'days_sober': 0, 'start_date': ''}
            }

    def setup_hundred_days(self):
        """تنظیم چالش 100 روزه"""
        if not self.hundred_days:
            for i in range(1, 101):
                self.hundred_days[str(i)] = False

    def create_app(self):
        """ایجاد برنامه Streamlit"""
        st.title("🎓 برنامه‌ریز درسی مهندسی پزشکی")
        
        # تب‌ها
        tab1, tab2, tab3, tab4 = st.tabs([
            "📅 برنامه هفتگی", 
            "📝 کارهای روزانه", 
            "✅ عادت‌ها", 
            "🎯 چالش 100 روز"
        ])

        with tab1:
            self.create_weekly_tab()
        
        with tab2:
            self.create_daily_tab()
        
        with tab3:
            self.create_habits_tab()
        
        with tab4:
            self.create_hundred_days_tab()

    def create_weekly_tab(self):
        """تب برنامه هفتگی"""
        st.header("برنامه هفتگی دانشگاه")
        
        # انتخاب نوع هفته
        week_type = st.radio("نوع هفته:", ["هفته زوج", "هفته فرد"], horizontal=True)
        current_week = self.even_week_schedule if week_type == "هفته زوج" else self.odd_week_schedule
        
        # فرم اضافه کردن درس
        with st.form("add_class_form"):
            st.subheader("اضافه کردن درس جدید")
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                day = st.selectbox("روز", ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه"])
            with col2:
                class_name = st.text_input("نام درس")
            with col3:
                start_time = st.text_input("ساعت شروع (مثلاً ۸:۰۰)")
            with col4:
                end_time = st.text_input("ساعت پایان (مثلاً ۱۰:۰۰)")
            with col5:
                class_week_type = st.selectbox("نوع هفته", ["زوج", "فرد", "هر هفته"])
            
            if st.form_submit_button("اضافه کردن درس"):
                if class_name and start_time and end_time:
                    class_info = {
                        'name': class_name,
                        'start': start_time,
                        'end': end_time
                    }
                    
                    if class_week_type == "زوج" or class_week_type == "هر هفته":
                        self.even_week_schedule[day].append(class_info)
                    if class_week_type == "فرد" or class_week_type == "هر هفته":
                        self.odd_week_schedule[day].append(class_info)
                    
                    self.save_data()
                    st.success("درس با موفقیت اضافه شد!")
                    st.rerun()
        
        # نمایش برنامه هفتگی
        st.subheader(f"برنامه {week_type}")
        days = ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه"]
        
        cols = st.columns(7)
        for i, day in enumerate(days):
            with cols[i]:
                st.subheader(day)
                classes = current_week[day]
                if not classes:
                    st.info("بدون کلاس")
                else:
                    for cls in sorted(classes, key=lambda x: x['start']):
                        st.success(f"{cls['name']}\n{cls['start']} - {cls['end']}")

    def create_daily_tab(self):
        """تب کارهای روزانه"""
        st.header("کارهای روزانه")
        
        # فرم اضافه کردن کار
        with st.form("add_task_form"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                task_title = st.text_input("عنوان کار")
            with col2:
                task_duration = st.number_input("مدت زمان (دقیقه)", min_value=1, max_value=480, value=30)
            with col3:
                task_priority = st.selectbox("اولویت", ["کم", "متوسط", "زیاد"])
            
            if st.form_submit_button("اضافه کردن کار"):
                if task_title:
                    task = {
                        'id': len(self.daily_tasks) + 1,
                        'title': task_title,
                        'duration': task_duration,
                        'priority': task_priority,
                        'completed': False,
                        'created_at': datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    self.daily_tasks.append(task)
                    self.save_data()
                    st.success("کار با موفقیت اضافه شد!")
                    st.rerun()
        
        # نمایش کارها
        st.subheader("لیست کارها")
        if not self.daily_tasks:
            st.info("هیچ کاری ثبت نشده است")
        else:
            # مرتب کردن کارها
            priority_order = {"زیاد": 3, "متوسط": 2, "کم": 1}
            sorted_tasks = sorted(self.daily_tasks, 
                                 key=lambda x: (not x['completed'], priority_order.get(x['priority'], 0)), 
                                 reverse=True)
            
            for task in sorted_tasks:
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    status = "✅" if task['completed'] else "⏳"
                    st.write(f"{status} **{task['title']}** - {task['duration']} دقیقه")
                
                with col2:
                    st.write(f"اولویت: {task['priority']}")
                
                with col3:
                    if not task['completed']:
                        if st.button("انجام شد", key=f"complete_{task['id']}"):
                            task['completed'] = True
                            self.save_data()
                            st.rerun()
                
                with col4:
                    if st.button("حذف", key=f"delete_{task['id']}"):
                        self.daily_tasks = [t for t in self.daily_tasks if t['id'] != task['id']]
                        self.save_data()
                        st.rerun()

    def create_habits_tab(self):
        """تب عادت‌ها"""
        st.header("مدیریت عادت‌ها")
        
        tab1, tab2 = st.tabs(["👍 عادت‌های مثبت", "👎 عادت‌های منفی"])
        
        with tab1:
            st.subheader("عادت‌های مثبت - زنجیروار")
            
            # فرم اضافه کردن عادت جدید
            with st.form("add_positive_habit"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    new_habit = st.text_input("عادت مثبت جدید")
                with col2:
                    if st.form_submit_button("اضافه کردن"):
                        if new_habit.strip():
                            self.positive_habits[new_habit.strip()] = {'streak': 0, 'history': []}
                            self.save_data()
                            st.success("عادت اضافه شد!")
                            st.rerun()
            
            # نمایش عادت‌های مثبت
            for habit, data in self.positive_habits.items():
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**{habit}** - زنجیره: {data['streak']} روز")
                
                with col2:
                    if st.button("تیک امروز ✅", key=f"positive_{habit}"):
                        today = date.today().isoformat()
                        if today not in data['history']:
                            data['history'].append(today)
                            data['streak'] += 1
                            self.save_data()
                            st.success(f"عادت {habit} برای امروز ثبت شد!")
                            st.rerun()
                
                with col3:
                    if st.button("حذف", key=f"delete_positive_{habit}"):
                        del self.positive_habits[habit]
                        self.save_data()
                        st.rerun()
        
        with tab2:
            st.subheader("عادت‌های منفی - روزشمار ترک")
            
            # فرم اضافه کردن عادت جدید
            with st.form("add_negative_habit"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    new_habit = st.text_input("عادت منفی جدید")
                with col2:
                    if st.form_submit_button("اضافه کردن"):
                        if new_habit.strip():
                            self.negative_habits[new_habit.strip()] = {'days_sober': 0, 'start_date': ''}
                            self.save_data()
                            st.success("عادت اضافه شد!")
                            st.rerun()
            
            # نمایش عادت‌های منفی
            for habit, data in self.negative_habits.items():
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    days_sober = data['days_sober']
                    start_date = data.get('start_date', 'شروع نشده')
                    st.write(f"**{habit}** - {days_sober} روز پاک")
                    st.caption(f"از {start_date}")
                
                with col2:
                    if st.button("شروع ترک", key=f"negative_{habit}"):
                        today = date.today().isoformat()
                        data['start_date'] = today
                        data['days_sober'] = 0
                        self.save_data()
                        st.success(f"ترک عادت {habit} شروع شد!")
                        st.rerun()
                
                with col3:
                    if st.button("حذف", key=f"delete_negative_{habit}"):
                        del self.negative_habits[habit]
                        self.save_data()
                        st.rerun()

    def create_hundred_days_tab(self):
        """تب چالش 100 روز"""
        st.header("چالش 100 روزه موفقیت")
        st.info("هر روز که به هدفمت پایبند می‌مونی، یک مربع رو تیک بزن!")
        
        # آمار
        completed = sum(1 for day in self.hundred_days.values() if day)
        remaining = 100 - completed
        percentage = (completed / 100) * 100
        
        st.subheader(f"پیشرفت: {completed} روز از 100 روز ({percentage:.1f}%)")
        
        # نوار پیشرفت
        st.progress(percentage / 100)
        
        # چارت 100 روزه
        st.subheader("چارت 100 روزه")
        
        # ایجاد جدول 10x10
        for row in range(10):
            cols = st.columns(10)
            for col in range(10):
                day_num = row * 10 + col + 1
                day_key = str(day_num)
                is_completed = self.hundred_days.get(day_key, False)
                
                with cols[col]:
                    if st.button(
                        str(day_num),
                        key=f"day_{day_num}",
                        type="primary" if is_completed else "secondary",
                        use_container_width=True
                    ):
                        self.hundred_days[day_key] = not self.hundred_days[day_key]
                        self.save_data()
                        st.rerun()

def main():
    app = StudyPlanner()

if __name__ == "__main__":
    main()
