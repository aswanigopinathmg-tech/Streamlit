import streamlit as st
import pandas as pd
from datetime import datetime, date
import json
import base64
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go

# Configure page
st.set_page_config(
    page_title="Soul & Water App",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)


# PWA Configuration
import streamlit as st
def add_pwa_config():
    st.markdown("""
    <!-- Android / Chrome -->
    <link rel="manifest" href="https://raw.githubusercontent.com/aswanigopinathmg-tech/Streamlit/main/manifest.json">

    <!-- iOS / Safari -->
  <link rel="apple-touch-icon" sizes="180x180" href="https://raw.githubusercontent.com/aswanigopinathmg-tech/Streamlit/main/ios-img-180.png">
    <link rel="apple-touch-icon" sizes="152x152" href="https://raw.githubusercontent.com/aswanigopinathmg-tech/Streamlit/main/ios-img-152.png">
    <link rel="apple-touch-icon" sizes="120x120" href="https://raw.githubusercontent.com/aswanigopinathmg-tech/Streamlit/main/ios-img-120.png">
    """, unsafe_allow_html=True)

# Call the function at the top of your Streamlit script
add_pwa_config()


# Custom CSS for responsive design
st.markdown("""
<script>
const manifestUrl = "https://raw.githubusercontent.com/aswanigopinathmg-tech/Streamlit/main/manifest.json";
const link = document.createElement('link');
link.rel = 'manifest';
link.href = manifestUrl;
document.head.appendChild(link);
</script>
""", unsafe_allow_html=True)


# Initialize session state
def initialize_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'customer_id' not in st.session_state:
        st.session_state.customer_id = None
    if 'submissions_df' not in st.session_state:
        st.session_state.submissions_df = pd.DataFrame(columns=[
            'submission_id', 'technician_id', 'technician_name', 'customer_id',
            'customer_name', 'test_type', 'parameters', 'timestamp', 'status',
            'approval_notes', 'approved_by'
        ])


# User credentials and mappings
USERS = {
    # Technicians
    'tech1': {'password': 'pass123', 'role': 'technician', 'name': 'John Doe',
              'customers': ['CUST001', 'CUST002', 'CUST003']},
    'tech2': {'password': 'pass456', 'role': 'technician', 'name': 'Jane Smith', 'customers': ['CUST004', 'CUST005']},

    # Managers
    'manager1': {'password': 'mgr123', 'role': 'manager', 'name': 'Bob Wilson'},
    'manager2': {'password': 'mgr456', 'role': 'manager', 'name': 'Alice Johnson'},

    # Customers
    'customer1': {'password': 'cust123', 'role': 'customer', 'name': 'ABC Corp', 'customer_id': 'CUST001'},
    'customer2': {'password': 'cust456', 'role': 'customer', 'name': 'XYZ Ltd', 'customer_id': 'CUST002'},
    'customer3': {'password': 'cust789', 'role': 'customer', 'name': 'Tech Solutions', 'customer_id': 'CUST003'},
    'customer4': {'password': 'cust321', 'role': 'customer', 'name': 'Green Energy', 'customer_id': 'CUST004'},
    'customer5': {'password': 'cust654', 'role': 'customer', 'name': 'Eco Systems', 'customer_id': 'CUST005'},
}

CUSTOMER_NAMES = {
    'CUST001': 'ABC Corp',
    'CUST002': 'XYZ Ltd',
    'CUST003': 'Tech Solutions',
    'CUST004': 'Green Energy',
    'CUST005': 'Eco Systems'
}

# Parameter validation ranges
PARAMETER_RANGES = {
    'soil_ph': {'acceptable': (6.0, 8.0), 'approval': (5.5, 8.5), 'unit': 'pH'},
    'soil_ec': {'acceptable': (0.1, 2.0), 'approval': (0.05, 3.0), 'unit': 'dS/m'},
    'water_ph': {'acceptable': (6.5, 8.5), 'approval': (6.0, 9.0), 'unit': 'pH'},
    'water_ec': {'acceptable': (0.1, 1.5), 'approval': (0.05, 2.0), 'unit': 'dS/m'},
    # Full suite parameters
    'nitrogen': {'acceptable': (10, 50), 'approval': (5, 70), 'unit': 'mg/kg'},
    'phosphorus': {'acceptable': (15, 80), 'approval': (10, 100), 'unit': 'mg/kg'},
    'potassium': {'acceptable': (100, 400), 'approval': (80, 500), 'unit': 'mg/kg'},
    'organic_matter': {'acceptable': (2.0, 6.0), 'approval': (1.0, 8.0), 'unit': '%'},
    'calcium': {'acceptable': (200, 800), 'approval': (150, 1000), 'unit': 'mg/kg'},
    'magnesium': {'acceptable': (50, 200), 'approval': (30, 250), 'unit': 'mg/kg'},
    'sulfur': {'acceptable': (10, 30), 'approval': (5, 40), 'unit': 'mg/kg'},
    'iron': {'acceptable': (20, 100), 'approval': (10, 150), 'unit': 'mg/kg'},
    'manganese': {'acceptable': (5, 50), 'approval': (2, 80), 'unit': 'mg/kg'},
    'zinc': {'acceptable': (1, 10), 'approval': (0.5, 15), 'unit': 'mg/kg'},
    'copper': {'acceptable': (1, 5), 'approval': (0.5, 8), 'unit': 'mg/kg'},
    'boron': {'acceptable': (0.5, 2.0), 'approval': (0.2, 3.0), 'unit': 'mg/kg'},
    'chloride': {'acceptable': (10, 100), 'approval': (5, 150), 'unit': 'mg/L'},
    'sodium': {'acceptable': (20, 200), 'approval': (10, 300), 'unit': 'mg/kg'},
    'cec': {'acceptable': (10, 30), 'approval': (5, 40), 'unit': 'cmol/kg'},
    'bulk_density': {'acceptable': (1.0, 1.6), 'approval': (0.8, 1.8), 'unit': 'g/cm³'},
}

BASIC_PARAMS = ['soil_ph', 'soil_ec', 'water_ph', 'water_ec']
FULL_SUITE_PARAMS = list(PARAMETER_RANGES.keys())


def validate_parameter(param_name, value):
    """Validate parameter value and return status"""
    if param_name not in PARAMETER_RANGES:
        return 'rejected', f'Unknown parameter: {param_name}'

    ranges = PARAMETER_RANGES[param_name]
    acceptable_min, acceptable_max = ranges['acceptable']
    approval_min, approval_max = ranges['approval']

    if acceptable_min <= value <= acceptable_max:
        return 'accepted', 'Value within acceptable range'
    elif approval_min <= value <= approval_max:
        return 'pending_approval', 'Value requires manager approval'
    else:
        return 'rejected', f'Value outside acceptable range ({approval_min}-{approval_max} {ranges["unit"]})'


def login_page():
    """Display login page"""
    st.markdown('<div class="main-header"><h1>🔬 Lab Management System</h1></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True):
            if username in USERS and USERS[username]['password'] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.user_role = USERS[username]['role']
                if USERS[username]['role'] == 'customer':
                    st.session_state.customer_id = USERS[username]['customer_id']
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials")

        # Demo credentials
        with st.expander("Demo Credentials"):
            st.write("**Technicians:**")
            st.write("- tech1 / pass123")
            st.write("- tech2 / pass456")
            st.write("**Managers:**")
            st.write("- manager1 / mgr123")
            st.write("**Customers:**")
            st.write("- customer1 / cust123")


def technician_interface():
    """Lab Technician Interface"""
    st.markdown('<div class="main-header"><h1>🔬 Lab Technician Interface</h1></div>', unsafe_allow_html=True)

    user_info = USERS[st.session_state.username]
    st.write(f"Welcome, **{user_info['name']}**")

    tab1, tab2 = st.tabs(["New Submission", "Submission History"])

    with tab1:
        st.subheader("New Test Submission")

        # Customer selection
        col1, col2 = st.columns(2)
        with col1:
            customer_id_option = st.selectbox(
                "Select Customer ID",
                options=[''] + user_info['customers'],
                key='customer_select'
            )

        with col2:
            # Manual customer ID entry option
            manual_customer_id = st.text_input("Or enter Customer ID manually")

        # Determine final customer ID
        final_customer_id = manual_customer_id if manual_customer_id else customer_id_option

        if final_customer_id:
            if final_customer_id not in user_info['customers']:
                st.error("❌ Customer ID not assigned to you or invalid")
                return

            customer_name = CUSTOMER_NAMES.get(final_customer_id, "Unknown Customer")
            st.success(f"✅ Customer: {customer_name}")

            # Test type selection
            test_type = st.radio("Select Test Type", ["Basic Test", "Full Suite"])

            # Parameter entry
            st.subheader("Enter Parameters")

            params = BASIC_PARAMS if test_type == "Basic Test" else FULL_SUITE_PARAMS
            parameter_values = {}

            # Create columns for better layout
            cols = st.columns(2)

            for i, param in enumerate(params):
                col = cols[i % 2]
                with col:
                    param_info = PARAMETER_RANGES[param]
                    label = param.replace('_', ' ').title()
                    unit = param_info['unit']

                    value = st.number_input(
                        f"{label} ({unit})",
                        min_value=0.0,
                        step=0.1,
                        key=f"param_{param}"
                    )
                    parameter_values[param] = value

            # Submission
            if st.button("Submit Test Results", use_container_width=True):
                if all(v > 0 for v in parameter_values.values()):
                    # Validate all parameters
                    all_statuses = {}
                    overall_status = 'accepted'
                    rejection_reasons = []

                    for param, value in parameter_values.items():
                        status, reason = validate_parameter(param, value)
                        all_statuses[param] = {'value': value, 'status': status, 'reason': reason}

                        if status == 'pending_approval' and overall_status == 'accepted':
                            overall_status = 'pending_approval'
                        elif status == 'rejected':
                            overall_status = 'rejected'
                            rejection_reasons.append(f"{param}: {reason}")

                    if overall_status == 'rejected':
                        st.error("❌ Submission rejected:")
                        for reason in rejection_reasons:
                            st.write(f"- {reason}")
                    else:
                        # Save submission
                        submission_id = len(st.session_state.submissions_df) + 1
                        new_submission = {
                            'submission_id': submission_id,
                            'technician_id': st.session_state.username,
                            'technician_name': user_info['name'],
                            'customer_id': final_customer_id,
                            'customer_name': customer_name,
                            'test_type': test_type,
                            'parameters': json.dumps(all_statuses),
                            'timestamp': datetime.now(),
                            'status': overall_status,
                            'approval_notes': '',
                            'approved_by': ''
                        }

                        st.session_state.submissions_df = pd.concat([
                            st.session_state.submissions_df,
                            pd.DataFrame([new_submission])
                        ], ignore_index=True)

                        if overall_status == 'accepted':
                            st.success("✅ Submission accepted and saved!")
                        else:
                            st.warning("⚠️ Submission saved but requires manager approval.")

                        st.rerun()
                else:
                    st.error("Please enter all parameter values")

    with tab2:
        st.subheader("Submission History")

        # Filters
        col1, col2 = st.columns(2)
        with col1:
            customer_filter = st.selectbox("Filter by Customer", ['All'] + user_info['customers'])
        with col2:
            date_filter = st.date_input("Filter by Date", value=None)

        # Get technician's submissions
        tech_submissions = st.session_state.submissions_df[
            st.session_state.submissions_df['technician_id'] == st.session_state.username
            ].copy()

        # Apply filters
        if customer_filter != 'All':
            tech_submissions = tech_submissions[tech_submissions['customer_id'] == customer_filter]

        if date_filter:
            tech_submissions = tech_submissions[
                tech_submissions['timestamp'].dt.date == date_filter
                ]

        if not tech_submissions.empty:
            # Display submissions
            for _, row in tech_submissions.iterrows():
                with st.expander(
                        f"Submission #{row['submission_id']} - {row['customer_name']} - {row['status'].upper()}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Customer:** {row['customer_name']}")
                        st.write(f"**Test Type:** {row['test_type']}")
                    with col2:
                        st.write(f"**Date:** {row['timestamp'].strftime('%Y-%m-%d %H:%M')}")
                        st.write(f"**Status:** {row['status']}")
                    with col3:
                        if row['status'] == 'rejected':
                            if st.button(f"Edit & Resubmit #{row['submission_id']}",
                                         key=f"edit_{row['submission_id']}"):
                                st.info("Edit functionality would be implemented here")

                    # Show parameters
                    params = json.loads(row['parameters'])
                    for param, details in params.items():
                        param_label = param.replace('_', ' ').title()
                        unit = PARAMETER_RANGES[param]['unit']
                        status_class = f"status-{details['status'].replace('_', '-')}"
                        st.markdown(f"**{param_label}:** {details['value']} {unit} "
                                    f'<span class="{status_class}">{details["status"]}</span>',
                                    unsafe_allow_html=True)
        else:
            st.info("No submissions found matching the criteria")


def manager_interface():
    """Lab Manager Interface"""
    st.markdown('<div class="main-header"><h1>👨‍💼 Lab Manager Interface</h1></div>', unsafe_allow_html=True)

    user_info = USERS[st.session_state.username]
    st.write(f"Welcome, **{user_info['name']}**")

    tab1, tab2, tab3 = st.tabs(["Approval Dashboard", "All Submissions", "Customer Health"])

    with tab1:
        st.subheader("Pending Approvals")

        pending_submissions = st.session_state.submissions_df[
            st.session_state.submissions_df['status'] == 'pending_approval'
            ].copy()

        if not pending_submissions.empty:
            for _, row in pending_submissions.iterrows():
                with st.expander(f"Submission #{row['submission_id']} - {row['customer_name']} - Pending Approval"):
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.write(f"**Technician:** {row['technician_name']}")
                        st.write(f"**Customer:** {row['customer_name']}")
                        st.write(f"**Test Type:** {row['test_type']}")
                        st.write(f"**Date:** {row['timestamp'].strftime('%Y-%m-%d %H:%M')}")

                        # Show parameters needing approval
                        params = json.loads(row['parameters'])
                        for param, details in params.items():
                            if details['status'] == 'pending_approval':
                                param_label = param.replace('_', ' ').title()
                                unit = PARAMETER_RANGES[param]['unit']
                                st.warning(f"**{param_label}:** {details['value']} {unit} - {details['reason']}")

                    with col2:
                        notes = st.text_area(f"Notes", key=f"notes_{row['submission_id']}")

                        col_approve, col_reject = st.columns(2)
                        with col_approve:
                            if st.button("✅ Approve", key=f"approve_{row['submission_id']}", use_container_width=True):
                                # Update submission status
                                idx = st.session_state.submissions_df[
                                    st.session_state.submissions_df['submission_id'] == row['submission_id']
                                    ].index[0]

                                st.session_state.submissions_df.loc[idx, 'status'] = 'accepted'
                                st.session_state.submissions_df.loc[idx, 'approval_notes'] = notes
                                st.session_state.submissions_df.loc[idx, 'approved_by'] = user_info['name']

                                st.success(f"Submission #{row['submission_id']} approved!")
                                st.rerun()

                        with col_reject:
                            if st.button("❌ Reject", key=f"reject_{row['submission_id']}", use_container_width=True):
                                idx = st.session_state.submissions_df[
                                    st.session_state.submissions_df['submission_id'] == row['submission_id']
                                    ].index[0]

                                st.session_state.submissions_df.loc[idx, 'status'] = 'rejected'
                                st.session_state.submissions_df.loc[idx, 'approval_notes'] = notes
                                st.session_state.submissions_df.loc[idx, 'approved_by'] = user_info['name']

                                st.success(f"Submission #{row['submission_id']} rejected!")
                                st.rerun()
        else:
            st.info("No pending approvals")

    with tab2:
        st.subheader("All Submissions")

        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            tech_filter = st.selectbox("Filter by Technician",
                                       ['All'] + [k for k, v in USERS.items() if v['role'] == 'technician'])
        with col2:
            customer_filter = st.selectbox("Filter by Customer", ['All'] + list(CUSTOMER_NAMES.keys()))
        with col3:
            status_filter = st.selectbox("Filter by Status", ['All', 'accepted', 'pending_approval', 'rejected'])

        # Filter data
        filtered_df = st.session_state.submissions_df.copy()

        if tech_filter != 'All':
            filtered_df = filtered_df[filtered_df['technician_id'] == tech_filter]
        if customer_filter != 'All':
            filtered_df = filtered_df[filtered_df['customer_id'] == customer_filter]
        if status_filter != 'All':
            filtered_df = filtered_df[filtered_df['status'] == status_filter]

        # Display summary metrics
        if not filtered_df.empty:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Submissions", len(filtered_df))
            with col2:
                accepted_count = len(filtered_df[filtered_df['status'] == 'accepted'])
                st.metric("Accepted", accepted_count)
            with col3:
                pending_count = len(filtered_df[filtered_df['status'] == 'pending_approval'])
                st.metric("Pending", pending_count)
            with col4:
                rejected_count = len(filtered_df[filtered_df['status'] == 'rejected'])
                st.metric("Rejected", rejected_count)

            # Display table
            display_df = filtered_df[['submission_id', 'technician_name', 'customer_name',
                                      'test_type', 'timestamp', 'status']].copy()
            display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info("No submissions found")

    with tab3:
        st.subheader("Customer Health Monitoring")

        customer_search = st.selectbox("Select Customer", [''] + list(CUSTOMER_NAMES.keys()))

        if customer_search:
            customer_data = st.session_state.submissions_df[
                (st.session_state.submissions_df['customer_id'] == customer_search) &
                (st.session_state.submissions_df['status'] == 'accepted')
                ].copy()

            if not customer_data.empty:
                st.write(f"**Customer:** {CUSTOMER_NAMES[customer_search]}")
                st.write(f"**Total Tests:** {len(customer_data)}")

                # Show trends
                customer_data_sorted = customer_data.sort_values('timestamp')

                # Parameter trends
                if len(customer_data_sorted) > 1:
                    st.subheader("Parameter Trends")

                    # Create trend charts for key parameters
                    for param in BASIC_PARAMS:
                        param_values = []
                        dates = []

                        for _, row in customer_data_sorted.iterrows():
                            params = json.loads(row['parameters'])
                            if param in params:
                                param_values.append(params[param]['value'])
                                dates.append(row['timestamp'])

                        if len(param_values) > 1:
                            fig = px.line(x=dates, y=param_values,
                                          title=f"{param.replace('_', ' ').title()} Trend",
                                          labels={'x': 'Date', 'y': f"{param} ({PARAMETER_RANGES[param]['unit']})"})

                            # Add acceptable range bands
                            acceptable_min, acceptable_max = PARAMETER_RANGES[param]['acceptable']
                            fig.add_hline(y=acceptable_min, line_dash="dash", line_color="green",
                                          annotation_text="Min Acceptable")
                            fig.add_hline(y=acceptable_max, line_dash="dash", line_color="green",
                                          annotation_text="Max Acceptable")

                            st.plotly_chart(fig, use_container_width=True)

                # Recent submissions table
                st.subheader("Recent Submissions")
                recent_df = customer_data_sorted.tail(10)[
                    ['submission_id', 'test_type', 'timestamp', 'technician_name']]
                recent_df['timestamp'] = recent_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
                st.dataframe(recent_df, use_container_width=True)
            else:
                st.info("No accepted submissions found for this customer")


def customer_interface():
    """Customer Interface"""
    st.markdown('<div class="main-header"><h1>📊 Customer Portal</h1></div>', unsafe_allow_html=True)

    user_info = USERS[st.session_state.username]
    customer_id = user_info['customer_id']
    st.write(f"Welcome, **{user_info['name']}**")

    # Get customer's approved data only
    customer_data = st.session_state.submissions_df[
        (st.session_state.submissions_df['customer_id'] == customer_id) &
        (st.session_state.submissions_df['status'] == 'accepted')
        ].copy()

    if not customer_data.empty:
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Tests", len(customer_data))
        with col2:
            basic_tests = len(customer_data[customer_data['test_type'] == 'Basic Test'])
            st.metric("Basic Tests", basic_tests)
        with col3:
            full_tests = len(customer_data[customer_data['test_type'] == 'Full Suite'])
            st.metric("Full Suite Tests", full_tests)

        # Recent test results
        st.subheader("Recent Test Results")

        # Sort by timestamp, most recent first
        customer_data_sorted = customer_data.sort_values('timestamp', ascending=False)

        for _, row in customer_data_sorted.head(5).iterrows():
            with st.expander(
                    f"Test #{row['submission_id']} - {row['test_type']} - {row['timestamp'].strftime('%Y-%m-%d')}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Test Type:** {row['test_type']}")
                    st.write(f"**Date:** {row['timestamp'].strftime('%Y-%m-%d %H:%M')}")
                with col2:
                    st.write(f"**Technician:** {row['technician_name']}")

                # Display parameters
                params = json.loads(row['parameters'])
                param_cols = st.columns(2)
                col_idx = 0

                for param, details in params.items():
                    if details['status'] == 'accepted':  # Only show accepted parameters
                        param_label = param.replace('_', ' ').title()
                        unit = PARAMETER_RANGES[param]['unit']

                        with param_cols[col_idx % 2]:
                            # Color code based on acceptable range
                            acceptable_min, acceptable_max = PARAMETER_RANGES[param]['acceptable']
                            value = details['value']

                            if acceptable_min <= value <= acceptable_max:
                                st.success(f"**{param_label}:** {value} {unit}")
                            else:
                                st.warning(f"**{param_label}:** {value} {unit}")

                        col_idx += 1

        # Parameter trends
        if len(customer_data_sorted) > 1:
            st.subheader("Parameter Trends")

            # Let customer select which parameter to view
            available_params = set()
            for _, row in customer_data_sorted.iterrows():
                params = json.loads(row['parameters'])
                available_params.update(params.keys())

            selected_param = st.selectbox(
                "Select Parameter to View Trend",
                sorted(list(available_params)),
                format_func=lambda x: x.replace('_', ' ').title()
            )

            if selected_param:
                param_values = []
                dates = []

                for _, row in customer_data_sorted.sort_values('timestamp').iterrows():
                    params = json.loads(row['parameters'])
                    if selected_param in params and params[selected_param]['status'] == 'accepted':
                        param_values.append(params[selected_param]['value'])
                        dates.append(row['timestamp'])

                if len(param_values) > 1:
                    fig = px.line(x=dates, y=param_values,
                                  title=f"{selected_param.replace('_', ' ').title()} Trend",
                                  labels={'x': 'Date',
                                          'y': f"{selected_param} ({PARAMETER_RANGES[selected_param]['unit']})"})

                    # Add acceptable range bands
                    acceptable_min, acceptable_max = PARAMETER_RANGES[selected_param]['acceptable']
                    fig.add_hrect(y0=acceptable_min, y1=acceptable_max,
                                  fillcolor="green", opacity=0.2,
                                  annotation_text="Acceptable Range")

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Not enough data points to show trend")

        # Export functionality
        st.subheader("Export Data")
        if st.button("📄 Export as PDF Report", use_container_width=True):
            # Generate PDF report content
            report_content = generate_pdf_report(customer_data, user_info['name'])

            # Create download button
            st.download_button(
                label="Download PDF Report",
                data=report_content,
                file_name=f"lab_report_{customer_id}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )

        # Data table
        st.subheader("All Test Results")
        display_df = customer_data_sorted[['submission_id', 'test_type', 'timestamp', 'technician_name']].copy()
        display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
        display_df.columns = ['Test ID', 'Test Type', 'Date', 'Technician']
        st.dataframe(display_df, use_container_width=True)

    else:
        st.info("No test results available yet. Please contact your lab technician.")


def generate_pdf_report(customer_data, customer_name):
    """Generate PDF report content (simplified - in real implementation, use reportlab)"""
    report_text = f"""
LAB MANAGEMENT SYSTEM
Test Results Report

Customer: {customer_name}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Total Tests: {len(customer_data)}

RECENT TEST RESULTS:
"""

    for _, row in customer_data.head(10).iterrows():
        report_text += f"""
Test #{row['submission_id']} - {row['test_type']}
Date: {row['timestamp'].strftime('%Y-%m-%d %H:%M')}
Technician: {row['technician_name']}

Parameters:
"""
        params = json.loads(row['parameters'])
        for param, details in params.items():
            if details['status'] == 'accepted':
                param_label = param.replace('_', ' ').title()
                unit = PARAMETER_RANGES[param]['unit']
                report_text += f"  {param_label}: {details['value']} {unit}\n"

        report_text += "\n"

    return report_text.encode('utf-8')


def main():
    """Main application logic"""
    initialize_session_state()

    # Logout button in sidebar
    if st.session_state.logged_in:
        with st.sidebar:
            st.write(f"Logged in as: **{st.session_state.username}**")
            st.write(f"Role: **{st.session_state.user_role}**")

            if st.button("Logout", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

            # Add some sample data for demo
            if st.button("Load Sample Data", use_container_width=True):
                load_sample_data()
                st.success("Sample data loaded!")
                st.rerun()

    # Route to appropriate interface
    if not st.session_state.logged_in:
        login_page()
    elif st.session_state.user_role == 'technician':
        technician_interface()
    elif st.session_state.user_role == 'manager':
        manager_interface()
    elif st.session_state.user_role == 'customer':
        customer_interface()


def load_sample_data():
    """Load sample data for demonstration"""
    sample_data = [
        {
            'submission_id': 1,
            'technician_id': 'tech1',
            'technician_name': 'John Doe',
            'customer_id': 'CUST001',
            'customer_name': 'ABC Corp',
            'test_type': 'Basic Test',
            'parameters': json.dumps({
                'soil_ph': {'value': 7.2, 'status': 'accepted', 'reason': 'Value within acceptable range'},
                'soil_ec': {'value': 1.5, 'status': 'accepted', 'reason': 'Value within acceptable range'},
                'water_ph': {'value': 7.8, 'status': 'accepted', 'reason': 'Value within acceptable range'},
                'water_ec': {'value': 0.8, 'status': 'accepted', 'reason': 'Value within acceptable range'}
            }),
            'timestamp': datetime(2024, 1, 15, 10, 30),
            'status': 'accepted',
            'approval_notes': '',
            'approved_by': ''
        },
        {
            'submission_id': 2,
            'technician_id': 'tech1',
            'technician_name': 'John Doe',
            'customer_id': 'CUST002',
            'customer_name': 'XYZ Ltd',
            'test_type': 'Basic Test',
            'parameters': json.dumps({
                'soil_ph': {'value': 5.8, 'status': 'pending_approval', 'reason': 'Value requires manager approval'},
                'soil_ec': {'value': 2.2, 'status': 'pending_approval', 'reason': 'Value requires manager approval'},
                'water_ph': {'value': 7.0, 'status': 'accepted', 'reason': 'Value within acceptable range'},
                'water_ec': {'value': 1.2, 'status': 'accepted', 'reason': 'Value within acceptable range'}
            }),
            'timestamp': datetime(2024, 1, 16, 14, 20),
            'status': 'pending_approval',
            'approval_notes': '',
            'approved_by': ''
        },
        {
            'submission_id': 3,
            'technician_id': 'tech2',
            'technician_name': 'Jane Smith',
            'customer_id': 'CUST004',
            'customer_name': 'Green Energy',
            'test_type': 'Full Suite',
            'parameters': json.dumps({
                'soil_ph': {'value': 6.8, 'status': 'accepted', 'reason': 'Value within acceptable range'},
                'soil_ec': {'value': 1.1, 'status': 'accepted', 'reason': 'Value within acceptable range'},
                'water_ph': {'value': 7.5, 'status': 'accepted', 'reason': 'Value within acceptable range'},
                'water_ec': {'value': 0.9, 'status': 'accepted', 'reason': 'Value within acceptable range'},
                'nitrogen': {'value': 35, 'status': 'accepted', 'reason': 'Value within acceptable range'},
                'phosphorus': {'value': 45, 'status': 'accepted', 'reason': 'Value within acceptable range'},
                'potassium': {'value': 250, 'status': 'accepted', 'reason': 'Value within acceptable range'}
            }),
            'timestamp': datetime(2024, 1, 17, 9, 15),
            'status': 'accepted',
            'approval_notes': '',
            'approved_by': ''
        }
    ]

    st.session_state.submissions_df = pd.DataFrame(sample_data)


if __name__ == "__main__":
    main()
