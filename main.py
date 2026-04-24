import flet as ft

def main(page: ft.Page):
    # Configuração básica
    page.title = "Teste do Ap"
    page.bgcolor = ft.colors.BLACK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Se isso aqui aparecer, o problema era o código. Se ficar branco, o problema é o celular/Flet!
    texto_sucesso = ft.Text("Olá, Ap! A maldição da tela branca acabou!", size=25, color="green", weight="bold", text_align=ft.TextAlign.CENTER)
    
    page.add(texto_sucesso)

ft.app(target=main)
