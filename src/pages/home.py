import streamlit as st

def authenticated_menu():
    if 'logged_in' in st.session_state or st.session_state.logged_in:
        st.html("""
          <style>
            [alt=Logo] {
              height: 5rem;
            }
          </style>
                """)
        st.logo("C:\\Users\\Пользователь\\PycharmProjects\\Augmentation\\logo.png")
        st.sidebar.page_link("pages/home.py", label="Главная")
        st.sidebar.page_link("pages/app.py", label="Аугментация")
        st.sidebar.page_link("pages/aug_data.py", label="Аугментация датасета")
        st.sidebar.page_link("pages/add.py", label="Добавить датасет")
        st.sidebar.page_link("pages/my_data.py", label="Мои датасеты")

def welcome():
    st.markdown("""
            <style>
            .single-line {
                white-space: nowrap;
                font-size: 36px;
                font-weight: bold;
                text-align: center;
            }
            .description {
                text-align: center;
            }
            </style>
            <div class="single-line">Добро пожаловать в Аугментацию онлайн</div>
            <div class="description">Данное приложение создано для быстрого и комфортного аугментирования наборов изображений</div>
            """, unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="Главная", page_icon=":home:")
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.warning("Пожалуйста, войдите в аккаунт.")
        st.stop()
    welcome()
    authenticated_menu()

if __name__ == "__main__":
    main()