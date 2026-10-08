from pathlib import Path

from streamlit.testing.v1 import AppTest


APP = Path(__file__).resolve().parents[1] / "streamlit_app.py"


def test_dashboard_filters_and_comparison_render_without_errors():
    app = AppTest.from_file(str(APP), default_timeout=30).run()
    assert not app.exception
    assert [tab.label for tab in app.tabs][:3] == ["Dashboard", "Kiosk Compare", "Briefings"]
    app.selectbox(key="dashboard_range").select("Last 3 months").run()
    app.selectbox(key="dashboard_kiosk").select("Bowls & Buns").run()
    assert not app.exception
    assert "270" not in next(m.value for m in app.markdown if 'class="sn-kpis"' in m.value)
    comparison = next(table.value for table in app.dataframe if "Urgent findings" in table.value.columns)
    assert comparison["Kiosk"].tolist() == ["Bowls & Buns"]
    app.selectbox(key="dashboard_range").select("Custom").run()
    assert not app.exception
    assert app.date_input(key="dashboard_dates").value


def test_email_challenge_deep_link_selects_the_requested_claim():
    claim_id = "weekly-week-12-coastal-cafe-semantic-equipment-failure-equipment-failure"
    app = AppTest.from_file(str(APP), default_timeout=30)
    app.query_params["claim"] = claim_id
    app.query_params["action"] = "challenge"
    app.run()
    assert not app.exception
    assert next(s.value for s in app.selectbox if s.label == "Claim to review") == claim_id
    next(button for button in app.button if button.label == "Review challenge").click().run()
    assert not app.exception
    assert any("Enter the claim concern" in warning.value for warning in app.warning)
