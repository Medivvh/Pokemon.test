from BasePage import BasePage



class LoginPage(BasePage):
    Login_selector = '#root > div > main:nth-child(1) > section > div.login__content > form > div:nth-child(1) > input'
    Password_selector = '#password'
    Login_button_selector = '#root > div > main:nth-child(1) > section > div.login__content > form > button'

    def __init__(self, page):
        super().__init__(page)
        self._endpoint = ''

    def login(self, username, password):
        self.go_to_url()
        self.type_text_to_selector(self.Login_selector, username)
        self.type_text_to_selector(self.Password_selector, password)
        self.click_selector(self.Login_button_selector)
        self.assert_next_page_have_text('Покемоны')