import streamlit as st
from drive import DriveService
from auth import login_ui, register_ui
import webbrowser
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
from PIL import Image
from functools import lru_cache
import time
import pygame
from fpdf import FPDF
import tempfile
import os
import matplotlib.pyplot as plt



class ViolationMonitor:
    def __init__(self):
        self.current_date = datetime.now().strftime("%m/%d/%Y")
        self.current_violations = {}  # Track only current date violations
        self.alert_active = False
        self.initialize_sound()
        
    def initialize_sound(self):
        try:
            pygame.mixer.init()
            self.alert_sound = pygame.mixer.Sound("alert.wav")
        except:
            self.alert_sound = None
            print("Sound initialization failed - alerts will be silent")
            
    def check_for_new_violations(self, drive_services):
        new_violations = False
        violation_type = None
        current_date = datetime.now().strftime("%m/%d/%Y")
        
        # Only proceed if checking current date
        if current_date != self.current_date:
            print(f"Date changed from {self.current_date} to {current_date} - resetting counts")
            self.current_date = current_date
            self.current_violations = {}  # Reset counts for new day
            
        print(f"\n===== Checking for violations on {current_date} =====")
        
        for v_type, service in drive_services.items():
            # Get data and filter for current date only
            dates = service.get_available_dates(force_refresh=True)
            if not dates:
                continue
                
            # Find today's data only
            today_data = next((d for d in dates if d['display_date'] == current_date), None)
            if not today_data:
                today_count = 0
            else:
                today_count = today_data['images_uploaded']
            
            print(f"Current {v_type} violations: {today_count}")
            
            # Compare with previous count
            if v_type in self.current_violations:
                if today_count > self.current_violations[v_type]:
                    print(f"New {v_type} violations detected: {today_count - self.current_violations[v_type]} new")
                    new_violations = True
                    violation_type = v_type
            elif today_count > 0:  # First detection for this type
                print(f"Initial {v_type} violations detected: {today_count}")
                new_violations = True
                violation_type = v_type
            
            # Update current count
            self.current_violations[v_type] = today_count
        
        return new_violations, violation_type

    def trigger_alert(self, violation_type):
        if not self.alert_active:
            self.alert_active = True
            self.alert_violation_type = violation_type
            # Reset dismiss setup
            if hasattr(st.session_state, 'alert_dismiss_setup'):
                del st.session_state.alert_dismiss_setup

def display_alert():
    if st.session_state.get('monitor', None) and st.session_state.monitor.alert_active:
        violation_type = st.session_state.monitor.alert_violation_type
        readable_type = {
            'worker': 'Worker Safety',
            'fallen': 'Fallen Objects',
            'empty': 'Empty Bottles'
        }.get(violation_type, violation_type)
        
        # Add the alert CSS styling
        st.markdown("""
        <style>
            .alert-box {
                background-color: #ff4444 !important;
                color: white !important;
                padding: 15px;
                border-radius: 5px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.05); }
                100% { transform: scale(1); }
            }
            .alert-close-btn {
                background-color: #ff4444 !important;
                color: white !important;
                border: 2px solid white !important;
                font-size: 20px;
                padding: 0;
                margin: 0;
                width: 30px;
                height: 30px;
                border-radius: 50%;
            }
            .alert-close-btn:hover {
                background-color: #cc0000 !important;
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Create alert container
        alert_placeholder = st.empty()
        
        with alert_placeholder.container():
            # Play sound
            if st.session_state.monitor.alert_sound:
                try:
                    st.session_state.monitor.alert_sound.play()
                except:
                    pass
            
            cols = st.columns([0.9, 0.1])
            with cols[0]:
                st.markdown(f"""
                <div class="alert-box">
                    <h3>⚠️ New {readable_type} Violation Detected!</h3>
                    <p>New safety violation images have been added to the system.</p>
                    <p><small>Detected at: {datetime.now().strftime("%H:%M:%S")}</small></p>
                </div>
                """, unsafe_allow_html=True)
            
            with cols[1]:
                if st.button("✕", key="alert_close_btn", help="Dismiss alert", 
                           on_click=lambda: setattr(st.session_state.monitor, 'alert_active', False)):
                    if st.session_state.monitor.alert_sound:
                        try:
                            st.session_state.monitor.alert_sound.stop()
                        except:
                            pass
                    alert_placeholder.empty()
                    st.rerun()
        
        # Auto-dismiss after 20 seconds
        if not hasattr(st.session_state, 'alert_dismiss_setup'):
            st.session_state.alert_dismiss_setup = True
            st.markdown(f"""
            <script>
            setTimeout(function() {{
                var alertBtn = parent.document.querySelector('button[data-testid="baseButton-secondary"][title="✕"]');
                if (alertBtn) alertBtn.click();
            }}, 20000);
            </script>
            """, unsafe_allow_html=True)


def get_month_based_week(date_obj):
    month_start = date_obj.replace(day=1)
    
    first_saturday = month_start
    while first_saturday.weekday() != 5:
        first_saturday += timedelta(days=1)
    
    if date_obj < first_saturday:
        week_num = 1
    else:
        days_since_first_sat = (date_obj - first_saturday).days
        week_num = days_since_first_sat // 7 + 1
    
    return f"{date_obj.strftime('%Y-%m')}-W{week_num:02d}"

st.set_page_config(
    page_title="Safety Violation Portal",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="logo1.png"
)

def load_css():
    st.markdown("""
    <style>
        .metric-card {
            background-color: white;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .violation-count {
            font-size: 2rem;
            font-weight: bold;
            color: #dc3545;
        }
        .violation-subtype {
            font-size: 1.2rem;
            color: #6c757d;
            margin-bottom: 1rem;
        }
        [data-testid="stSidebar"] {
            background-color: #e9ecef !important;
        }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource(ttl=3600)
def init_drive_services():
    return {
        'worker': DriveService('Safety_Violation_System1', 'violation_metadata.json'),
        'fallen': DriveService('Fallen_Objects_System', 'fallen_metadata.json'),
        'empty': DriveService('Empty_Bottles_System', 'empty_bottles_metadata.json')
    }

def display_logo():
    try:
        logo = Image.open("logo1.png")
        st.sidebar.image(logo, use_container_width=True)
    except:
        st.sidebar.markdown("### Safety Violation Portal")

@lru_cache(maxsize=3)
def load_violation_data(violation_type):
    try:
        service = st.session_state.drive_services[{
            "Worker Violations": 'worker',
            "Fallen Objects": 'fallen', 
            "Empty Bottles": 'empty'
        }[violation_type]]
        
        dates = service.get_available_dates()
        if not dates:
            if violation_type == "Worker Violations":
                return None, None, None
            return None, None
            
        if violation_type == "Worker Violations":
            mask_data = []
            gloves_data = []
            
            for d in dates:
                date_obj = datetime.strptime(d['display_date'], "%m/%d/%Y")
                
                mask_data.append({
                    'display_date': d['display_date'],
                    'date': date_obj,
                    'violations_count': d.get('mask_count', 0),
                    'month': date_obj.strftime('%Y-%m'),
                    'week': get_month_based_week(date_obj),
                    'folder_id': d['folder_id']
                })
                
                gloves_data.append({
                    'display_date': d['display_date'],
                    'date': date_obj,
                    'violations_count': d.get('gloves_count', 0),
                    'month': date_obj.strftime('%Y-%m'),
                    'week': get_month_based_week(date_obj),
                    'folder_id': d['folder_id']
                })
            
            return pd.DataFrame(mask_data), pd.DataFrame(gloves_data), "Worker Safety"
        else:
            data = []
            for d in dates:
                date_obj = datetime.strptime(d['display_date'], "%m/%d/%Y")
                data.append({
                    'display_date': d['display_date'],
                    'date': date_obj,
                    'folder_id': d['folder_id'],
                    'violations_count': d['images_uploaded'],
                    'images_count': d['images_uploaded'],
                    'videos_count': d['videos_count'],
                    'month': date_obj.strftime('%Y-%m'),
                    'week': get_month_based_week(date_obj)
                })
            
            return pd.DataFrame(data), {
                "Fallen Objects": "Fallen Objects",
                "Empty Bottles": "Empty Bottles"
            }[violation_type]
        
    except Exception as e:
        st.error(f"Data loading failed: {str(e)}")
        if violation_type == "Worker Violations":
            return None, None, None
        return None, None

def calculate_metrics(df):
    df = df.sort_values('date')
    monthly = df.groupby('month', as_index=False)['violations_count'].sum()
    weekly = df.groupby('week', as_index=False)['violations_count'].sum()
    
    current_date = datetime.now()
    current_week = get_month_based_week(current_date)
    current_week_data = weekly[weekly['week'] == current_week]
    current_count = current_week_data['violations_count'].iloc[0] if not current_week_data.empty else 0
    
    week_ended = (current_date.weekday() >= 4)
    
    return {
        'total': df['violations_count'].sum(),
        'worst_month': monthly['violations_count'].max(),
        'worst_week': weekly['violations_count'].max(),
        'current_week_count': current_count,
        'week_ended': week_ended
    }

def render_metrics(df, violation_subtype=None):
    st.subheader("📊 Summary Statistics")
    if violation_subtype:
        st.markdown(f'<div class="violation-subtype">{violation_subtype} Violations</div>', unsafe_allow_html=True)
    
    metrics = calculate_metrics(df)
    
    cols = st.columns(3)
    labels = [
        "Total Violations",
        "Worst Month",
        "Worst Week"
    ]
    
    for col, (value, label) in zip(cols, zip(
        [metrics['total'], metrics['worst_month'], metrics['worst_week']],
        labels
    )):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="violation-count">{value}</div>
                <div class="violation-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

def render_trend_charts(df, violation_subtype=None):
    st.subheader("📈 Trend Analysis")
    if violation_subtype:
        st.markdown(f'<div class="violation-subtype">{violation_subtype} Violations</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Daily Trend", "Monthly Summary", "Weekly View"])
    
    with tab1:
        fig = px.bar(df.sort_values('date'), 
                    x='date', 
                    y='violations_count',
                    labels={'date': 'Date', 'violations_count': 'Violations'})
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        monthly = df.groupby('month', as_index=False)['violations_count'].sum()
        fig = px.bar(monthly, 
                    x='month', 
                    y='violations_count',
                    labels={'month': 'Month', 'violations_count': 'Violations'})
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        weekly = df.groupby('week', as_index=False)['violations_count'].sum()
        weekly['week_label'] = weekly['week'].apply(
            lambda x: f"{x.split('-')[0]}-{x.split('-')[1]} Week {int(x.split('-')[2][1:])}"
        )
        
        fig = px.line(weekly, 
                     x='week_label', 
                     y='violations_count', 
                     markers=True,
                     labels={'week_label': 'Week (Sat-Fri)', 'violations_count': 'Violations'})
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

def render_worker_violations(mask_df, gloves_df, title_prefix):
    st.title(title_prefix)
    
    selected_date = st.sidebar.selectbox(
        "📅 Select Date",
        options=mask_df['display_date'].tolist(),
        index=0
    )
    
    selected_mask_data = mask_df[mask_df['display_date'] == selected_date].iloc[0]
    selected_gloves_data = gloves_df[gloves_df['display_date'] == selected_date].iloc[0]
    folder_id = selected_mask_data['folder_id']
    
    if folder_id:
        if st.button("📂 Open Worker Violations in Drive", key="worker_drive_button"):
            webbrowser.open(f"https://drive.google.com/drive/folders/{folder_id}")
    
    tab1, tab2 = st.tabs(["Mask Violations", "Gloves Violations"])
    
    with tab1:
        render_metrics(mask_df, "Mask")
        render_trend_charts(mask_df, "Mask")
    
    with tab2:
        render_metrics(gloves_df, "Gloves")
        render_trend_charts(gloves_df, "Gloves")

def render_other_violations(df, title_prefix):
    selected_date = st.sidebar.selectbox(
        "📅 Select Date",
        options=df['display_date'].tolist(),
        index=0
    )
    selected_data = df[df['display_date'] == selected_date].iloc[0]

    st.title(f"{title_prefix} Violations - {selected_date}")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("📂 Open in Drive", type="primary"):
            webbrowser.open(f"https://drive.google.com/drive/folders/{selected_data['folder_id']}")
    
    with col2:
        vid_text = "video" if selected_data['videos_count'] == 1 else "videos"
        st.caption(f" {selected_data['images_count']} violation images | {selected_data['videos_count']} {vid_text} available")

    render_metrics(df)
    render_trend_charts(df)


def generate_report():
    """Generate a comprehensive PDF report with all violation data and visualizations"""
    # Initialize PDF with professional layout
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_draw_color(100, 100, 100)  # Gray border color
    
    # 1. Cover Page
    pdf.add_page()
    pdf.set_font('Arial', 'B', 24)
    pdf.cell(0, 20, 'SAFETY VIOLATION COMPREHENSIVE REPORT', 0, 1, 'C')
    pdf.ln(10)
    pdf.set_font('Arial', '', 14)
    pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, 'C')
    
    try:
        logo_path = "logo1.png"
        if os.path.exists(logo_path):
            pdf.image(logo_path, x=75, w=60)
    except:
        pass
    
    # 2. Load all data
    data = {
        'Worker Safety': {
            'mask': load_violation_data("Worker Violations")[0],
            'gloves': load_violation_data("Worker Violations")[1]
        },
        'Fallen Objects': load_violation_data("Fallen Objects")[0],
        'Empty Bottles': load_violation_data("Empty Bottles")[0]
    }

    # Convert dates to datetime objects
    for category in data:
        if category == 'Worker Safety':
            for subtype in data[category]:
                data[category][subtype]['date'] = pd.to_datetime(data[category][subtype]['date'])
        else:
            data[category]['date'] = pd.to_datetime(data[category]['date'])

    # 3. Executive Summary
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'EXECUTIVE SUMMARY', 0, 1)
    pdf.ln(5)
    
    # Calculate totals
    mask_total = data['Worker Safety']['mask']['violations_count'].sum()
    gloves_total = data['Worker Safety']['gloves']['violations_count'].sum()
    fallen_total = data['Fallen Objects']['violations_count'].sum()
    empty_total = data['Empty Bottles']['violations_count'].sum()
    
    # Custom table implementation for summary
    col_widths = [120, 70]
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(col_widths[0], 10, 'Violation Type', border=1)
    pdf.cell(col_widths[1], 10, 'Total Count', border=1, ln=1)
    
    pdf.set_font('Arial', '', 12)
    for label, value in [('Mask Violations', mask_total),
                        ('Gloves Violations', gloves_total),
                        ('Fallen Objects', fallen_total),
                        ('Empty Bottles', empty_total)]:
        pdf.cell(col_widths[0], 10, label, border=1)
        pdf.cell(col_widths[1], 10, str(value), border=1, ln=1)
    
    pdf.ln(15)
    
    # 4. Generate All Visualizations
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # ========================
            # Worker Safety Section
            # ========================
            pdf.add_page()
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'WORKER SAFETY VIOLATIONS', 0, 1)
            pdf.ln(5)
            
            # Daily Trends
            create_combo_chart(
                data['Worker Safety']['mask'], 
                data['Worker Safety']['gloves'],
                "Daily Worker Safety Violations",
                os.path.join(temp_dir, "worker_daily.png"),
                "Mask", "Gloves"
            )
            pdf.image(os.path.join(temp_dir, "worker_daily.png"), x=10, w=190)
            pdf.ln(5)
            
            # Weekly Trends
            mask_weekly = create_temporal_dataset(data['Worker Safety']['mask'], 'W')
            gloves_weekly = create_temporal_dataset(data['Worker Safety']['gloves'], 'W')
            create_combo_chart(
                mask_weekly,
                gloves_weekly,
                "Weekly Worker Safety Violations",
                os.path.join(temp_dir, "worker_weekly.png"),
                "Mask", "Gloves"
            )
            pdf.image(os.path.join(temp_dir, "worker_weekly.png"), x=10, w=190)
            pdf.ln(5)
            
            # Monthly Trends
            mask_monthly = create_temporal_dataset(data['Worker Safety']['mask'], 'M')
            gloves_monthly = create_temporal_dataset(data['Worker Safety']['gloves'], 'M')
            create_combo_chart(
                mask_monthly,
                gloves_monthly,
                "Monthly Worker Safety Violations",
                os.path.join(temp_dir, "worker_monthly.png"),
                "Mask", "Gloves"
            )
            pdf.image(os.path.join(temp_dir, "worker_monthly.png"), x=10, w=190)
            
            # ========================
            # Fallen Objects Section
            # ========================
            pdf.add_page()
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'FALLEN OBJECTS VIOLATIONS', 0, 1)
            pdf.ln(5)
            
            # Daily/Weekly/Monthly charts
            for timeframe, title_suffix in [('D', 'Daily'), ('W', 'Weekly'), ('M', 'Monthly')]:
                timeframe_data = create_temporal_dataset(data['Fallen Objects'], timeframe)
                create_single_chart(
                    timeframe_data,
                    f"{title_suffix} Fallen Objects Violations",
                    os.path.join(temp_dir, f"fallen_{timeframe.lower()}.png"),
                    color='#ff7f0e'
                )
                pdf.image(os.path.join(temp_dir, f"fallen_{timeframe.lower()}.png"), x=10, w=190)
                pdf.ln(5)
            
            # ========================
            # Empty Bottles Section
            # ========================
            pdf.add_page()
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'EMPTY BOTTLES VIOLATIONS', 0, 1)
            pdf.ln(5)
            
            # Daily/Weekly/Monthly charts
            for timeframe, title_suffix in [('D', 'Daily'), ('W', 'Weekly'), ('M', 'Monthly')]:
                timeframe_data = create_temporal_dataset(data['Empty Bottles'], timeframe)
                create_single_chart(
                    timeframe_data,
                    f"{title_suffix} Empty Bottles Violations",
                    os.path.join(temp_dir, f"empty_{timeframe.lower()}.png"),
                    color='#2ca02c'
                )
                pdf.image(os.path.join(temp_dir, f"empty_{timeframe.lower()}.png"), x=10, w=190)
                pdf.ln(5)
                
        except Exception as e:
            print(f"Visualization error: {str(e)}")
            pdf.set_font("Arial", size=10)
            pdf.cell(0, 10, "[Some visualizations skipped due to generation error]", 0, 1)

    # 5. Detailed Data Section
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'DETAILED VIOLATION RECORDS', 0, 1)
    pdf.ln(8)
    
    for category in data:
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, category.upper(), 0, 1)
        pdf.ln(5)
        
        if category == 'Worker Safety':
            for subtype in ['mask', 'gloves']:
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 8, f"{subtype.capitalize()} Violations:", 0, 1)
                _ = add_custom_table(pdf, data[category][subtype])
                pdf.ln(3)
        else:
            _ = add_custom_table(pdf, data[category])
            pdf.ln(5)

    # Finalize PDF
    pdf_path = os.path.join(tempfile.gettempdir(), 
                            f"Safety_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    pdf.output(pdf_path)
    st.session_state.report_path = pdf_path 

def add_custom_table(pdf, df):
    """Completely silent table implementation"""
    df = df.sort_values('date', ascending=False)
    df['running_total'] = df['violations_count'].cumsum()
    # Header
    pdf.set_fill_color(200, 200, 200)
    pdf.set_font('Arial', 'B', 10)
    _ = pdf.cell(60, 10, 'Date', border=1, fill=True)
    _ = pdf.cell(40, 10, 'Count', border=1, fill=True)
    _ = pdf.cell(40, 10, 'Running Total', border=1, fill=True, ln=1)
    # Data rows
    pdf.set_font('Arial', '', 9)
    fill = False
    for _, row in df.iterrows():
        _ = pdf.set_fill_color(240, 240, 240) if fill else pdf.set_fill_color(255, 255, 255)
        _ = pdf.cell(60, 10, row['date'].strftime('%Y-%m-%d'), border=1, fill=fill)
        _ = pdf.cell(40, 10, str(row['violations_count']), border=1, fill=fill)
        _ = pdf.cell(40, 10, str(row['running_total']), border=1, fill=fill, ln=1)
        fill = not fill

# Helper Functions
def create_temporal_dataset(df, freq):
    """Aggregate data by time frequency"""
    df = df.copy()
    df['period'] = df['date'].dt.to_period(freq)
    return df.groupby('period', as_index=False).agg({
        'violations_count': 'sum',
        'date': 'first'  # Keep first date of period for plotting
    })

def create_combo_chart(df1, df2, title, save_path, label1, label2):
    """Create dual-bar chart for comparison"""
    plt.figure(figsize=(12, 6))
    plt.bar(df1['date'], df1['violations_count'], 
           width=0.4, label=label1, alpha=0.7, color='#1f77b4')
    plt.bar(df2['date'] + pd.Timedelta(days=0.4), 
           df2['violations_count'],
           width=0.4, label=label2, alpha=0.7, color='#ff7f0e')
    plt.title(title, pad=20)
    plt.legend()
    plt.xticks(rotation=45)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=120, bbox_inches='tight')
    plt.close()

def create_single_chart(df, title, save_path, color):
    """Create single bar chart"""
    plt.figure(figsize=(12, 6))
    plt.bar(df['date'], df['violations_count'], 
           width=0.6, color=color, alpha=0.7)
    plt.title(title, pad=20)
    plt.xticks(rotation=45)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=120, bbox_inches='tight')
    plt.close()


def render_ui():
    st.sidebar.success(f"Welcome, {st.session_state.email.split('@')[0]}!")
    violation_type = st.sidebar.radio(
        "Select Violation Type",
        ("Worker Violations", "Fallen Objects", "Empty Bottles"),
        index=0
    )

    with st.spinner("Loading data..."):
        if violation_type == "Worker Violations":
            mask_df, gloves_df, title_prefix = load_violation_data(violation_type)
            if mask_df is None or gloves_df is None:
                st.warning("No worker violation data found")
                if st.sidebar.button("🚪 Logout"):
                    st.session_state.clear()
                    st.rerun()
                return
            
            # Add report button column
            col1, col2 = st.columns([3, 1])
            with col1:
                render_worker_violations(mask_df, gloves_df, title_prefix)
            with col2:
                if st.button("📊 Generate Report"):
                    with st.spinner("Generating report..."):
                        generate_report()  # No return value captured
                        if 'report_path' in st.session_state:
                            with open(st.session_state.report_path, "rb") as f:
                                st.download_button(
                                    label="⬇️ Download Report",
                                    data=f,
                                    file_name=f"Safety_Violation_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
                                    mime="application/pdf"
                                )
        else:
            df, title_prefix = load_violation_data(violation_type)
            if df is None or df.empty:
                st.warning(f"No {violation_type.lower()} data found")
                if st.sidebar.button("🚪 Logout"):
                    st.session_state.clear()
                    st.rerun()
                return
            
            # Add report button column
            col1, col2 = st.columns([3, 1])
            with col1:
                render_other_violations(df, title_prefix)
            with col2:
                if st.button("📊 Generate Report"):
                    with st.spinner("Generating report..."):
                        report_path = generate_report()
                        with open(report_path, "rb") as f:
                            st.download_button(
                                label="⬇️ Download Report",
                                data=f,
                                file_name=f"Safety_Violation_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
                                mime="application/pdf"
                            )
    
    if st.sidebar.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()

def handle_auth():
    if 'page' not in st.session_state:
        st.session_state.page = "Login"
    if st.session_state.page == "Login":
        login_ui()
    else:
        register_ui()

def init_services():
    if 'drive_services' not in st.session_state:
        with st.spinner("Loading..."):
            st.session_state.drive_services = init_drive_services()

def main():
    load_css()
    
    if not st.session_state.get('logged_in', False):
        handle_auth()
        return
    
    # Initialize monitor if not exists
    if 'monitor' not in st.session_state:
        print("Initializing new violation monitor")
        st.session_state.monitor = ViolationMonitor()
    
    # Check for new violations periodically
    if 'last_check_time' not in st.session_state:
        st.session_state.last_check_time = time.time()
    
    current_time = time.time()
    if current_time - st.session_state.last_check_time > 30:  # Check every 30 seconds
        print(f"\n=== Performing violation check at {datetime.fromtimestamp(current_time).strftime('%H:%M:%S')} ===")
        
        if st.session_state.get('drive_services'):
            new_violations, violation_type = st.session_state.monitor.check_for_new_violations(st.session_state.drive_services)
            if new_violations:
                print(f"\n=== Triggering {violation_type} alert ===")
                st.session_state.monitor.trigger_alert(violation_type)
                st.rerun()  # Force UI update
        
        st.session_state.last_check_time = current_time
    
    # Display alert if active
    display_alert()
    
    display_logo()
    init_services()
    render_ui()

if __name__ == "__main__":
    main()