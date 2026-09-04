import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="Retail Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Apply the global design system
from ui.theme import apply_global_css
apply_global_css()

# 3. Imports for page views & sidebar
from ui.layout import render_app_header, render_footer
from ui.sidebar import render_sidebar
from ui.views_executive import render_executive_overview
from ui.views_sales import render_sales_analytics
from ui.views_customers import render_customer_analytics
from ui.views_category import render_category_and_product
from ui.views_stores import render_store_performance
from ui.views_anomaly import render_anomaly_detection
from ui.views_ai_analyst import render_ai_analyst
from ui.views_quality import render_data_quality
from ui.views_about import render_about_page


def main():
    st.session_state.setdefault("page", "executive")

    try:
        # Render sidebar & get filtered data
        selected_page, filtered_df, val_report = render_sidebar()
    except Exception as e:
        st.error(f"Failed to load dataset: {e}")
        st.info("Try uploading a different dataset or check the schema mapping on the Data Quality page.")
        return

    score = val_report.get("score", 0) if val_report else 0
    records = len(filtered_df) if not filtered_df.empty else 0
    render_app_header(dataset_name=st.session_state.get("dataset_label", "Retail Data"),
                      records=records, quality_score=score)

    # Route to the selected page
    try:
        if selected_page == "executive":
            render_executive_overview(filtered_df)
        elif selected_page == "sales":
            render_sales_analytics(filtered_df)
        elif selected_page == "customers":
            render_customer_analytics(filtered_df)
        elif selected_page == "category":
            render_category_and_product(filtered_df)
        elif selected_page == "stores":
            render_store_performance(filtered_df)
        elif selected_page == "anomaly":
            render_anomaly_detection(filtered_df)
        elif selected_page == "ai":
            render_ai_analyst(filtered_df)
        elif selected_page == "quality":
            render_data_quality(st.session_state.get("full_dataset", filtered_df), val_report)
        elif selected_page == "about":
            render_about_page()
    except Exception as e:
        st.error(f"Error rendering page: {e}")
        st.info("Please check the dataset and filters. If the issue persists, try reloading the page.")

    render_footer()


if __name__ == "__main__":
    main()