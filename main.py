import flet as ft

def main(page: ft.Page):
    page.title = "Diário da Joana"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F3E5F5"
    page.window_width = 400
    page.window_height = 800
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO

    ROXO_FORTE = "#4A148C"
    ROXO_CLARO = "#9C27B0"
    BRANCO = ft.colors.WHITE

    def mostrar_mensagem(texto, cor_fundo=ft.colors.GREEN_700):
        page.snack_bar = ft.SnackBar(ft.Text(texto, color=BRANCO, weight=ft.FontWeight.BOLD), bgcolor=cor_fundo)
        page.snack_bar.open = True
        page.update()

    # --- TELAS FALSAS (MOCK) SÓ PARA TESTAR O VISUAL ---
    tela_turmas = ft.Container(content=ft.Text("Tela de Turmas", color=ROXO_FORTE, size=20, weight="bold"), alignment=ft.alignment.center, visible=False)
    tela_alunos = ft.Container(content=ft.Text("Tela de Alunos", color=ROXO_FORTE, size=20, weight="bold"), alignment=ft.alignment.center, visible=False)
    tela_materias = ft.Container(content=ft.Text("Tela de Matérias", color=ROXO_FORTE, size=20, weight="bold"), alignment=ft.alignment.center, visible=False)
    tela_chamada = ft.Container(content=ft.Text("Tela de Chamada", color=ROXO_FORTE, size=20, weight="bold"), alignment=ft.alignment.center, visible=False)
    tela_notas = ft.Container(content=ft.Text("Tela de Notas", color=ROXO_FORTE, size=20, weight="bold"), alignment=ft.alignment.center, visible=False)
    tela_relatorios = ft.Container(content=ft.Text("Tela de Relatórios", color=ROXO_FORTE, size=20, weight="bold"), alignment=ft.alignment.center, visible=False)
    tela_boletim = ft.Container(content=ft.Text("Tela de Boletins", color=ROXO_FORTE, size=20, weight="bold"), alignment=ft.alignment.center, visible=False)
    tela_config = ft.Container(content=ft.Text("Configurações", color=ROXO_FORTE, size=20, weight="bold"), alignment=ft.alignment.center, visible=False)

    telas = {"home": None, "turmas": tela_turmas, "alunos": tela_alunos, "materias": tela_materias, "chamada": tela_chamada, "notas": tela_notas, "relatorios": tela_relatorios, "boletim": tela_boletim, "config": tela_config}

    def abrir_tela(nome_tela):
        for nome, container in telas.items():
            if container: container.visible = (nome == nome_tela)
        page.update()

    def criar_atalho(icone, texto, acao, cor_fundo=BRANCO, cor_icone=ROXO_FORTE):
        return ft.Container(content=ft.Column([ft.Icon(name=icone, size=40, color=cor_icone), ft.Text(texto, size=16, weight=ft.FontWeight.BOLD, color=cor_icone)], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5), bgcolor=cor_fundo, width=150, height=120, border_radius=15, border=ft.border.all(1, ROXO_CLARO), shadow=ft.BoxShadow(spread_radius=1, blur_radius=5, color=ft.colors.BLACK12, offset=ft.Offset(0, 2)), ink=True, on_click=lambda e: abrir_tela(acao))

    telas["home"] = ft.Container(content=ft.Column([
        ft.Container(content=ft.Column([ft.CircleAvatar(radius=50, bgcolor=ROXO_FORTE, content=ft.Icon(ft.icons.FACE_RETOUCHING_NATURAL, size=50, color=BRANCO)), ft.Text("Diário da Joana - MODO VISUAL", size=22, weight=ft.FontWeight.BOLD, color=ROXO_FORTE)], horizontal_alignment=ft.CrossAxisAlignment.CENTER), padding=ft.padding.only(top=20, bottom=20)),
        ft.Divider(),
        ft.Row([criar_atalho(ft.icons.FACT_CHECK, "Chamada", "chamada", "#E1BEE7", ROXO_FORTE), criar_atalho(ft.icons.ASSESSMENT, "Boletins", "boletim", "#E1BEE7", ROXO_FORTE)], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([criar_atalho(ft.icons.CLASS_, "Turmas", "turmas"), criar_atalho(ft.icons.PEOPLE, "Alunos", "alunos")], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([criar_atalho(ft.icons.EDIT_DOCUMENT, "Notas", "notas"), criar_atalho(ft.icons.MENU_BOOK, "Matérias", "materias")], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([criar_atalho(ft.icons.PICTURE_AS_PDF, "Relatórios", "relatorios"), criar_atalho(ft.icons.SETTINGS, "Config.", "config")], alignment=ft.MainAxisAlignment.CENTER),
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER), visible=True)

    def mudar_aba_inferior(index):
        if index == 0: abrir_tela("home")
        elif index == 1: abrir_tela("turmas")
        elif index == 2: abrir_tela("alunos")

    barra_navegacao = ft.Container(content=ft.Row([
        ft.Container(content=ft.Column([ft.Icon(name=ft.icons.HOME, color=BRANCO, size=26), ft.Text("Início", color=BRANCO, size=12, weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2), expand=True, ink=True, on_click=lambda e: mudar_aba_inferior(0)), 
        ft.Container(content=ft.Column([ft.Icon(name=ft.icons.CLASS_OUTLINED, color=BRANCO, size=26), ft.Text("Turmas", color=BRANCO, size=12, weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2), expand=True, ink=True, on_click=lambda e: mudar_aba_inferior(1)), 
        ft.Container(content=ft.Column([ft.Icon(name=ft.icons.PEOPLE, color=BRANCO, size=26), ft.Text("Alunos", color=BRANCO, size=12, weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2), expand=True, ink=True, on_click=lambda e: mudar_aba_inferior(2))
    ], alignment=ft.MainAxisAlignment.SPACE_AROUND), bgcolor=ROXO_FORTE, height=65, padding=ft.padding.only(top=5, bottom=5))

    topo = ft.Container(content=ft.Text("App da Professora", color=BRANCO, weight=ft.FontWeight.BOLD, size=18), bgcolor=ROXO_FORTE, padding=15, alignment=ft.alignment.center)
    conteudo_principal = ft.Container(content=ft.Column([telas["home"], tela_turmas, tela_alunos, tela_materias, tela_chamada, tela_notas, tela_relatorios, tela_boletim, tela_config], expand=True, scroll=ft.ScrollMode.AUTO), expand=True)
    
    page.add(ft.Column([topo, conteudo_principal, barra_navegacao], expand=True, spacing=0))
    mostrar_mensagem("Interface rodando lisa!", ft.colors.GREEN_700)

ft.app(target=main)
