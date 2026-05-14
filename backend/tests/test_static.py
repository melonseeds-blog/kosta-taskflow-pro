def test_index_html_served_at_root(client):
    response = client.get("/")
    assert response.status_code == 200
    content_type = response.headers.get("content-type", "")
    assert "text/html" in content_type
    assert "TaskFlow Pro" in response.text


def test_app_js_served(client):
    response = client.get("/app.js")
    assert response.status_code == 200
    content_type = response.headers.get("content-type", "")
    assert "javascript" in content_type


def test_index_includes_dayjs_cdn(client):
    # 03-design #9: dayjs + ko locale + relativeTime plugin 이 모두 로드되어야 함
    body = client.get("/").text
    assert "dayjs.min.js" in body
    assert "locale/ko.js" in body
    assert "plugin/relativeTime.js" in body
