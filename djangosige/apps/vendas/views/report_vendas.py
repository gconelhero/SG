# -*- coding: utf-8 -*-
from djangosige.apps.vendas.models import OrcamentoVenda, PedidoVenda, ItensVenda, Pagamento
from djangosige.apps.cadastro.models import MinhaEmpresa
from djangosige.apps.login.models import User
from djangosige.configs.settings import MEDIA_ROOT

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import cm
from reportlab.lib.utils import simpleSplit
from reportlab.platypus import PageBreak
from datetime import datetime
import io
import locale


class ReportVenda:

    def __init__(self, title, venda, user_id):
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF8')
        self.buffer = io.BytesIO()
        self.plot = canvas.Canvas(self.buffer, pagesize=A4)
        self.plot.translate(cm, cm)

        self.title = title
        self.plot.setTitle(title)
        
        if isinstance(venda, OrcamentoVenda):
            self.venda = OrcamentoVenda.objects.get(pk=venda.pk)
        if isinstance(venda, PedidoVenda):
            self.venda = PedidoVenda.objects.get(pk=venda.pk)
        self.user_id = user_id
        
        self.title_font_name = 'Times-Bold'
        self.subtitle_font_name = 'Times-Bold'
        self.itens_font_name = 'Times-Roman'
        self.title_font_size = 13
        self.subtitle_font_size = 12
        self.itens_font_size = 9
        self.total_font_size = 11
        self.eixo_x = 200
        self.eixo_y = 780

    def new_page(self):
        self.rodape(False)
        self.plot.showPage()
        self.eixo_y = 800
        self.plot.translate(cm, cm)        


    def header(self):
        try:   
            usuario = User.objects.get(pk=self.user_id)
            m_empresa = MinhaEmpresa.objects.get(m_usuario=usuario.id)
            flogo = m_empresa.m_empresa.logo_file
            logo_path = '{0}{1}'.format(MEDIA_ROOT, flogo.name)
            self.plot.drawInlineImage(logo_path, 40, 727, width=100,height=80)
        except:
            print("Logo tipo ou usuário vinculado a empresa não encontrados.")
            pass
        
        self.plot.setFont("Times-Bold", 16)
        if isinstance(self.venda, OrcamentoVenda):
            self.eixo_x = 190
            self.plot.drawString(self.eixo_x, self.eixo_y, self.title)
            self.plot.setFont("Helvetica", 9)
            self.eixo_x += 45
            self.eixo_y -= 15
            self.plot.drawString(self.eixo_x, self.eixo_y, f"Data: {self.venda.data_emissao.strftime('%d/%m/%Y')}")
            if self.venda.data_vencimento != None:    
                self.eixo_x -= 23
                self.eixo_y -= 15
                self.plot.drawString(self.eixo_x, self.eixo_y, f"Data vencimento: {self.venda.data_vencimento.strftime('%d/%m/%Y')}")
        if isinstance(self.venda, PedidoVenda):
            self.plot.drawString(self.eixo_x, self.eixo_y, self.title)
            self.plot.setFont("Helvetica", 9)
            self.eixo_x += 35
            self.eixo_y -= 15
            self.plot.drawString(self.eixo_x, self.eixo_y, f"Data: {self.venda.data_emissao.strftime('%d/%m/%Y')}")
        
        self.plot.line(0, 720, 535, 720)


    def cliente(self):
        cliente = self.venda.cliente
        self.plot.setFont("Times-Bold", 13)
        self.eixo_x = 6
        self.eixo_y = 700
        if self.venda.fazenda != None:
            self.venda.cliente.nome_razao_social = f"{self.venda.cliente.nome_razao_social} \
                                                    {self.venda.fazenda.nome_impressao_nota}"
            if len(self.venda.cliente.nome_razao_social) > 20:
                line = simpleSplit(self.venda.cliente.nome_razao_social, 
                                    fontName='Times-Bold', fontSize=13, maxWidth=20)
                if len(' '.join(line[:-2])) < 20:
                    self.plot.drawString(self.eixo_x, self.eixo_y, str(' '.join(line[:-2])))
                    self.eixo_y -= 10
                    self.plot.drawString(self.eixo_x, self.eixo_y, str(''.join(line[-2:])))
                else:
                    self.plot.drawString(self.eixo_x, self.eixo_y, str(' '.join(line[:-3])))
                    self.eixo_y -= 10
                    self.plot.drawString(self.eixo_x, self.eixo_y, str(' '.join(line[-3:])))
            else:
                self.plot.drawString(self.eixo_x, self.eixo_y, str(self.venda.cliente.nome_razao_social))
        elif self.venda.fazenda == None:
            if len(self.venda.cliente.nome_razao_social) > 20:
                line = simpleSplit(self.venda.cliente.nome_razao_social, 
                                    fontName='Times-Bold', fontSize=13, maxWidth=20)
                if len(' '.join(line[:-1])) < 20:
                    self.plot.drawString(self.eixo_x, self.eixo_y, str(' '.join(line[:-1])))
                    self.eixo_y -= 10
                    self.plot.drawString(self.eixo_x, self.eixo_y, str(''.join(line[-1])))
                else:
                    self.plot.drawString(self.eixo_x, self.eixo_y, str(' '.join(line[:-2])))
                    self.eixo_y -= 10
                    self.plot.drawString(self.eixo_x, self.eixo_y, str(' '.join(line[-2:])))
            else:
                self.plot.drawString(self.eixo_x, self.eixo_y, str(self.venda.cliente.nome_razao_social))
        
        self.eixo_y -= 20
        self.plot.setFont("Times-Roman", 10)
        if self.venda.fazenda != None:
            self.plot.drawString(6, self.eixo_y, f"Endereço: {self.venda.fazenda.endereco} - {self.venda.fazenda.bairro}")    
            self.eixo_y -= 15
            self.plot.drawString(6, self.eixo_y,f"Cidade: {self.venda.fazenda.municipio}")
            self.plot.drawString(230, self.eixo_y,f"UF: {self.venda.fazenda.uf}")
            self.plot.drawString(430, self.eixo_y, f"CEP: {self.venda.fazenda.cep}")
            self.eixo_y -= 15
        else:
            self.plot.drawString(6, self.eixo_y, f"Endereço: {self.venda.cliente.endereco_padrao.logradouro},\
                                 {self.venda.cliente.endereco_padrao.numero} - {self.venda.cliente.endereco_padrao.bairro}")
            self.eixo_y -= 15
            self.plot.drawString(6, self.eixo_y,f"Cidade: {self.venda.cliente.endereco_padrao.municipio}")
            self.plot.drawString(230, self.eixo_y,f"UF: {self.venda.cliente.endereco_padrao.uf}")
            self.plot.drawString(430, self.eixo_y, f"CEP: {self.venda.cliente.endereco_padrao.cep}")
            self.eixo_y -= 15
        if self.venda.cliente.telefone_padrao != None:
            self.plot.drawString(6, self.eixo_y,f"Tel: {self.venda.cliente.telefone_padrao.telefone}")
        if self.venda.cliente.email_padrao != None:
            self.plot.drawString(230, self.eixo_y,f"E-mail: {self.venda.cliente.email_padrao.email}")

        self.plot.setFont("Times-Bold", 11)
        if self.venda.cliente.tipo_pessoa == 'PJ':
            self.plot.drawString(230, 700, f"CNPJ: {self.venda.cliente.pessoa_jur_info.cnpj}")
            self.plot.drawString(430, 700, f"IE: {self.venda.cliente.pessoa_jur_info.inscricao_estadual}")
        else:
            self.plot.drawString(230, 700, f"CPF: {self.venda.cliente.pessoa_fis_info.cpf}")
            if self.venda.fazenda != None:
                self.plot.drawString(430, 700, f"IE: {self.venda.fazenda.inscricao_estadual}")        
            else:
                self.plot.drawString(430, 700, f"RG: {self.venda.cliente.pessoa_fis_info.rg}")

        self.eixo_y -= 20
        self.plot.line(0, self.eixo_y, 535, self.eixo_y)

        
    def produtos(self):
        itens = ItensVenda.objects.filter(venda_id=self.venda)
        self.plot.setFont("Times-Bold", 13)
        self.eixo_y -= 20
        self.plot.drawString(243, self.eixo_y, "Produtos")
        
        self.plot.setFont("Times-Bold", 12)
        self.eixo_x = 6 # Horizontal
        self.eixo_y -= 30
        self.plot.drawString(self.eixo_x, self.eixo_y, "Código")
        self.eixo_x += 52
        self.plot.drawString(self.eixo_x, self.eixo_y, "Descrição / Produto")
        self.eixo_x += 152
        self.plot.drawString(self.eixo_x, self.eixo_y, "Qtde")
        self.eixo_x += 48
        self.plot.drawString(self.eixo_x, self.eixo_y, "UN")
        self.eixo_x += 40
        self.plot.drawString(self.eixo_x, self.eixo_y, "Valor unitário")
        self.eixo_x += 90
        self.plot.drawString(self.eixo_x, self.eixo_y, "Desconto")
        self.eixo_x += 80
        self.plot.drawString(self.eixo_x, self.eixo_y, "Subtotal")

        self.plot.setFont(self.itens_font_name, self.itens_font_size)
        self.eixo_x = 7
        self.eixo_y -= 25
        for i in itens:
            codigo = i.produto.codigo
            descricao = i.produto.descricao
            quantidade = i.quantidade
            unidade = i.produto.unidade.sigla_unidade
            valor_unit = locale.currency(i.valor_unit, grouping=True)
            if str(i.tipo_desconto) == '1':
                i.desconto = float(i.valor_unit) * int(i.quantidade) / 100.00 * float(i.desconto)
            desconto = locale.currency(i.desconto, grouping=True)
            subtotal = locale.currency(i.subtotal, grouping=True)
            self.plot.drawString(self.eixo_x, self.eixo_y, str(codigo))
            self.eixo_x += 52
            if len(descricao) > 30:
                line = simpleSplit(descricao, fontName=self.itens_font_name, 
                                    fontSize=self.itens_font_size, maxWidth=20)
                if len(' '.join(line[:-1])) < 30:
                    self.plot.drawString(self.eixo_x, self.eixo_y, str(' '.join(line[:-1])))
                    self.eixo_y -= 10
                    self.plot.drawString(self.eixo_x, self.eixo_y, str(''.join(line[-1])))
                    self.eixo_y += 10
                else:
                    self.plot.drawString(self.eixo_x, self.eixo_y, str(' '.join(line[:-2])))
                    self.eixo_y -= 10
                    self.plot.drawString(self.eixo_x, self.eixo_y, str(' '.join(line[-2:])))
                    self.eixo_y += 10
            else:
                self.plot.drawString(self.eixo_x, self.eixo_y, str(descricao))
            self.eixo_x += 155
            self.plot.drawString(self.eixo_x, self.eixo_y, str(quantidade))
            self.eixo_x += 46
            self.plot.drawString(self.eixo_x, self.eixo_y, str(unidade))
            self.eixo_x += 50
            self.plot.drawString(self.eixo_x, self.eixo_y, str(valor_unit))
            self.eixo_x += 82
            self.plot.drawString(self.eixo_x, self.eixo_y, str(desconto))
            self.eixo_x += 80
            self.plot.drawString(self.eixo_x, self.eixo_y, str(subtotal))
            
            self.eixo_y -= 30
            self.eixo_x = 7

            # Abrindo uma nova página!!
            if self.eixo_y < 50:
                self.new_page()
                self.plot.setFont("Times-Bold", 12)
                self.eixo_x = 6 # Horizontal
                self.eixo_y -= 30
                self.plot.drawString(self.eixo_x, self.eixo_y, "Código")
                self.eixo_x += 52
                self.plot.drawString(self.eixo_x, self.eixo_y, "Descrição / Produto")
                self.eixo_x += 152
                self.plot.drawString(self.eixo_x, self.eixo_y, "Qtde")
                self.eixo_x += 48
                self.plot.drawString(self.eixo_x, self.eixo_y, "UN")
                self.eixo_x += 40
                self.plot.drawString(self.eixo_x, self.eixo_y, "Valor unitário")
                self.eixo_x += 90
                self.plot.drawString(self.eixo_x, self.eixo_y, "Desconto")
                self.eixo_x += 80
                self.plot.drawString(self.eixo_x, self.eixo_y, "Subtotal")

                self.plot.setFont(self.itens_font_name, self.itens_font_size)
                self.eixo_x = 7
                self.eixo_y -= 25
                        

        self.eixo_y -= 20
        self.plot.line(0, self.eixo_y, 535, self.eixo_y)

    
    def totais(self):
        self.sem_div = False
        if self.eixo_y < 170:
            self.new_page()
        if self.eixo_y <= 220:
            self.sem_div = True

        self.plot.setFont(self.title_font_name, self.title_font_size)
        self.eixo_y -= 20
        self.plot.drawString(243, self.eixo_y, "Totais")

        self.plot.setFont(self.subtitle_font_name, self.subtitle_font_size)
        self.eixo_x = 38
        self.eixo_y -= 30
        self.plot.drawString(self.eixo_x, self.eixo_y, "Frete")
        self.eixo_x += 100
        self.plot.drawString(self.eixo_x, self.eixo_y, "Seguro")
        self.eixo_x += 100
        self.plot.drawString(self.eixo_x, self.eixo_y, "Despesas")
        self.eixo_x += 100
        self.plot.drawString(self.eixo_x, self.eixo_y, "Desconto")
        self.eixo_x += 100
        self.plot.drawString(self.eixo_x, self.eixo_y, "Impostos")

        frete = locale.currency(self.venda.frete, grouping=True)
        seguro = locale.currency(self.venda.seguro, grouping=True)
        despesas = locale.currency(self.venda.despesas, grouping=True)
        if str(self.venda.tipo_desconto) == '1':
            self.venda.desconto = (self.venda.valor_total / 100) * self.venda.desconto
        desconto = locale.currency(self.venda.desconto, grouping=True)
        impostos = locale.currency(self.venda.impostos, grouping=True)
        total_sem_impostos = locale.currency(self.venda.valor_total - self.venda.impostos, grouping=True)
        total = locale.currency(self.venda.valor_total, grouping=True)

        self.plot.setFont(self.itens_font_name, self.itens_font_size)
        self.eixo_x = 37
        self.eixo_y -= 20
        self.plot.drawString(self.eixo_x, self.eixo_y, str(frete))
        self.eixo_x += 103
        self.plot.drawString(self.eixo_x, self.eixo_y, str(seguro))
        self.eixo_x += 102
        self.plot.drawString(self.eixo_x, self.eixo_y, str(despesas))
        self.eixo_x += 100
        self.plot.drawString(self.eixo_x, self.eixo_y, str(desconto))
        self.eixo_x += 100
        self.plot.drawString(self.eixo_x, self.eixo_y, str(impostos))

        self.eixo_y -= 20
        self.plot.line(0, self.eixo_y, 535, self.eixo_y)

        self.plot.setFont(self.itens_font_name, self.total_font_size)
        self.eixo_y -= 20
        self.plot.drawString(260, self.eixo_y, "Total sem impostos:")
        self.plot.drawString(460, self.eixo_y, str(total_sem_impostos))
        self.eixo_y -= 5
        self.plot.line(250, self.eixo_y, 535, self.eixo_y)
        self.plot.setFont(self.title_font_name, self.total_font_size)
        self.eixo_y -= 13
        self.plot.drawString(322, self.eixo_y, "Total:")
        self.plot.drawString(460, self.eixo_y, str(total))

        self.eixo_y -= 40
        if self.sem_div == False:
            self.plot.line(0, self.eixo_y, 535, self.eixo_y)
        else:
            pass
    
    
    def pagamento(self):
        if self.sem_div == True:
            self.plot.line(0, self.eixo_y, 535, self.eixo_y)
            self.sem_div = False
        pagamento = Pagamento.objects.filter(venda_id=self.venda)
        self.plot.setFont(self.title_font_name, self.title_font_size)
        self.eixo_y -= 20
        self.plot.drawString(229, self.eixo_y, "Pagamento")

        self.plot.setFont(self.itens_font_name, self.itens_font_size)
        self.eixo_x = 10
        self.plot.drawString(self.eixo_x, self.eixo_y, f"Forma pagamento: {self.venda.cond_pagamento.get_forma_display()}")
        self.eixo_y -= 10
        self.plot.drawString(self.eixo_x, self.eixo_y, f"Nº de parcelas: {self.venda.cond_pagamento.n_parcelas}")
        self.plot.setFont(self.subtitle_font_name, self.subtitle_font_size)
        self.eixo_x = 100
        self.eixo_y -= 30
        self.plot.drawString(self.eixo_x, self.eixo_y, "Parcela")
        self.eixo_x += 130  
        self.plot.drawString(self.eixo_x, self.eixo_y, "Vencimento")
        self.eixo_x += 130
        self.plot.drawString(self.eixo_x, self.eixo_y, "Valor")

        self.plot.setFont(self.itens_font_name, self.itens_font_size)
        self.eixo_y -= 25
        for i in pagamento:
            parcela = i.indice_parcela
            data = i.vencimento.strftime('%d/%m/%Y')
            valor = locale.currency(i.valor_parcela, grouping=True)
            self.eixo_x = 115
            self.plot.drawString(self.eixo_x, self.eixo_y, str(parcela))
            self.eixo_x += 125
            self.plot.drawString(self.eixo_x, self.eixo_y, str(data))
            self.eixo_x += 118
            self.plot.drawString(self.eixo_x, self.eixo_y, str(valor))
            self.eixo_y -= 15
            if self.eixo_y < 20:
                self.new_page()
                self.plot.setFont(self.subtitle_font_name, self.subtitle_font_size)
                self.eixo_x = 100
                self.eixo_y -= 30
                self.plot.drawString(self.eixo_x, self.eixo_y, "Parcela")
                self.eixo_x += 130
                self.plot.drawString(self.eixo_x, self.eixo_y, "Vencimento")
                self.eixo_x += 130
                self.plot.drawString(self.eixo_x, self.eixo_y, "Valor")

                self.plot.setFont(self.itens_font_name, self.itens_font_size)
                self.eixo_y -= 25
        if self.eixo_y < 30:
            self.new_page()
            self.sem_div = True
        if self.sem_div == False:
            self.plot.line(0, self.eixo_y, 535, self.eixo_y)

    
    def obs(self):
        if self.eixo_y < 80:
            self.new_page()
        if self.sem_div == True:
            self.plot.line(0, self.eixo_y, 535, self.eixo_y)
        self.plot.setFont(self.title_font_name, self.title_font_size)
        self.eixo_x = 6
        self.eixo_y -= 20
        self.plot.drawString(225, self.eixo_y, "Observações")
        obs = self.venda.observacoes
        if obs == None:
            obs = 'Sem observações.'
        self.eixo_y -= 20
        self.plot.setFont(self.itens_font_name, self.total_font_size)
        self.plot.drawString(self.eixo_x, self.eixo_y, str(obs))
        self.eixo_y -= 20
        self.plot.drawString(self.eixo_x, self.eixo_y, f"Vendedor: {self.venda.vendedor}")
        for i in range(0, 2):
            self.plot.drawString(self.eixo_x, self.eixo_y, "")
            self.eixo_y -= 10
        

        
    def rodape(self, flag):
        self.plot.line(0, 10, 535, 10)
        self.plot.setFont("Times-Roman", 9)
        self.plot.drawString(0, 0, 'Gerado por SG CS')
        self.plot.setFont("Times-Roman", 8)
        self.plot.drawString(430, 0, f"Data de impressão: {datetime.now().strftime('%d/%m/%Y')}")
        if flag == True:
            return self.response()

    def response(self):
        self.plot.save()
        self.buffer.seek(0)
        
        return self.buffer