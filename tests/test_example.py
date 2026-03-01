from pom_project.pages.home_page import HomePage


def test_navigate_example(page, app_url: str) -> None:
    home_page = HomePage(page)

    home_page.goto(app_url)
    home_page.expect_title("Example Domain")
    home_page.expect_header_text("Example Domain")
