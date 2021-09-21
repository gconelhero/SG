# -*- coding: utf-8 -*-

from django.views.generic import View
from django.http import HttpResponse
from django.core import serializers

from djangosige.apps.cadastro.models import Pessoa, Fazenda, Cliente, Fornecedor, Transportadora, Produto, Endereco
from djangosige.apps.fiscal.models import ICMS, ICMSSN, IPI, ICMSUFDest, GrupoFiscal
from djangosige.apps.vendas.models import CondicaoPagamento

import json

class InfoCliente(View):

    def post(self, request, *args, **kwargs):
        obj_list = []
        pessoa = Pessoa.objects.get(pk=request.POST['pessoaId'])
        cliente = Cliente.objects.get(pk=request.POST['pessoaId'])
        fazendas = Fazenda.objects.all().filter(pessoa_faz=request.POST['pessoaId'])
        enderecos = Endereco.objects.all().filter(pessoa_end=request.POST['pessoaId'])

        if fazendas:
            obj_list += [faz for faz in fazendas]
        if request.POST['fazendaId'] and fazendas:
            fazenda = Fazenda.objects.get(pk=request.POST['fazendaId'])
        else:
            fazenda = ''
        if fazenda != '':
            obj_list.append(fazenda)
        
        if enderecos:
            obj_list += [end for end in enderecos]
        if request.POST['enderecoId'] and enderecos:
            endereco = Endereco.objects.get(pk=request.POST['enderecoId'])
        
        obj_list.append(cliente)

        if pessoa.endereco_padrao:
            obj_list.append(pessoa.endereco_padrao)
        if pessoa.email_padrao:
            obj_list.append(pessoa.email_padrao)
        if pessoa.telefone_padrao:
            obj_list.append(pessoa.telefone_padrao)
        if pessoa.tipo_pessoa == 'PJ':
            obj_list.append(pessoa.pessoa_jur_info)
        elif pessoa.tipo_pessoa == 'PF':
            obj_list.append(pessoa.pessoa_fis_info)
        
        data = serializers.serialize('json', obj_list, fields=('indicador_ie', 'limite_de_credito', 'cnpj', 'inscricao_estadual', 'responsavel', 'cpf', 'rg', 'id_estrangeiro', 'logradouro', 'numero', 'bairro',
                                                            'municipio', 'cmun', 'uf', 'pais', 'complemento', 'cep', 'email', 'telefone','fazenda', 'nome','endereco', 'complemento', 'tipo_endereco'))
        
        return HttpResponse(data, content_type='application/json')


class InfoFornecedor(View):

    def post(self, request, *args, **kwargs):
        obj_list = []
        pessoa = Pessoa.objects.get(pk=request.POST['pessoaId'])
        fornecedor = Fornecedor.objects.get(pk=request.POST['pessoaId'])
        obj_list.append(fornecedor)

        if pessoa.endereco_padrao:
            obj_list.append(pessoa.endereco_padrao)
        if pessoa.email_padrao:
            obj_list.append(pessoa.email_padrao)
        if pessoa.telefone_padrao:
            obj_list.append(pessoa.telefone_padrao)

        if pessoa.tipo_pessoa == 'PJ':
            obj_list.append(pessoa.pessoa_jur_info)
        elif pessoa.tipo_pessoa == 'PF':
            obj_list.append(pessoa.pessoa_fis_info)

        data = serializers.serialize('json', obj_list, fields=('indicador_ie', 'limite_de_credito', 'cnpj', 'inscricao_estadual', 'responsavel', 'cpf', 'rg', 'id_estrangeiro', 'logradouro', 'numero', 'bairro',
                                                               'municipio', 'cmun', 'uf', 'pais', 'complemento', 'cep', 'email', 'telefone',))

        return HttpResponse(data, content_type='application/json')


class InfoEmpresa(View):

    def post(self, request, *args, **kwargs):
        pessoa = Pessoa.objects.get(pk=request.POST['pessoaId'])
        obj_list = []
        obj_list.append(pessoa.pessoa_jur_info)

        if pessoa.endereco_padrao:
            obj_list.append(pessoa.endereco_padrao)

        data = serializers.serialize('json', obj_list, fields=('cnpj', 'inscricao_estadual', 'logradouro', 'numero', 'bairro',
                                                               'municipio', 'cmun', 'uf', 'pais', 'complemento', 'cep',))
        
        return HttpResponse(data, content_type='application/json')


class InfoTransportadora(View):

    def post(self, request, *args, **kwargs):
        veiculos = Transportadora.objects.get(
            pk=request.POST['transportadoraId']).veiculo.all()
        data = serializers.serialize(
            'json', veiculos, fields=('id', 'descricao',))

        return HttpResponse(data, content_type='application/json')


class InfoProduto(View):

    def post(self, request, *args, **kwargs):
        obj_list = []
        try:
            produto = Produto.objects.get(pk=request.POST['produtoId'])
            obj_list.append(produto)

            if request.POST['grupoFiscalId'] != '' and list(request.POST.keys())[0] == 'grupoFiscalId':
                grupo_fiscal = GrupoFiscal.objects.get(id=request.POST['grupoFiscalId'])
                produto.grupo_fiscal = grupo_fiscal
            
            elif request.POST['grupoFiscalId'] == '' and list(request.POST.keys())[0] == 'grupoFiscalId':
                produto.grupo_fiscal = None
            
            if list(request.POST.keys())[0] == 'produtoId':
                grupo_fiscal = produto.grupo_fiscal
                post_change = request.POST.copy()
                if grupo_fiscal != None:
                    post_change['grupoFiscalId'] = grupo_fiscal.id
                    request.POST = post_change
                
        except Exception as erro:
            print("ERRO -> NÃO EXISTE PRODUTO", erro)
            produto = None
            pass

        try:
            if produto.grupo_fiscal:
                if produto.grupo_fiscal.regime_trib == '0':
                    icms, created = ICMS.objects.get_or_create(
                        grupo_fiscal=produto.grupo_fiscal)
                else:
                    icms, created = ICMSSN.objects.get_or_create(
                        grupo_fiscal=produto.grupo_fiscal)

                ipi, created = IPI.objects.get_or_create(
                    grupo_fiscal=produto.grupo_fiscal)
                icms_dest, created = ICMSUFDest.objects.get_or_create(
                    grupo_fiscal=produto.grupo_fiscal)
                
                obj_list.append(icms)
                obj_list.append(ipi)
                obj_list.append(icms_dest)
                if request.POST['grupoFiscalId'] != '':
                    grupo_fiscal = GrupoFiscal.objects.get(id=request.POST['grupoFiscalId'])
            
            data = serializers.serialize('json', obj_list, fields=('venda', 'controlar_estoque', 'estoque_atual', 'grupo_fiscal', 'cfop_padrao',
                                                                'tipo_ipi', 'p_ipi', 'valor_fixo', 'p_icms', 'p_red_bc', 'p_icmsst', 'p_red_bcst', 'p_mvast',
                                                                'p_fcp_dest', 'p_icms_dest', 'p_icms_inter', 'p_icms_inter_part',
                                                                'ipi_incluido_preco', 'incluir_bc_icms', 'incluir_bc_icmsst', 'icmssn_incluido_preco',
                                                                'icmssnst_incluido_preco', 'icms_incluido_preco', 'icmsst_incluido_preco'))

            return HttpResponse(data, content_type='application/json')
            
        except Exception as erro:
            print(erro, "PRODUTO NÃO ENCONTRADO")
            pass


class SelectFormProduto(View):

    def get(self, request, *args, **kwargs):
        produtos = []
        obj_list = []
        if request.is_ajax():
            term = request.GET.get('term')
            if term != None:
                q_one = Produto.objects.all().filter(codigo__icontains=term)
                q_two = Produto.objects.all().filter(descricao__icontains=term)
                produtos = [prod for prod in q_one.union(q_two)]
            else:
                produtos = [prod for prod in Produto.objects.all()]

            obj_list = [{'id': i.id, 'codigo': i.codigo, 'descricao': i.descricao} for i in produtos]

        else:
            return HttpResponse('Utilização incorreta.')
        
        return HttpResponse(json.dumps(obj_list), content_type='application/json')


class SelectFormCliente(View):

    def get(self, request, *args, **kwargs):
        obj_list = []
        if request.is_ajax():
            term = request.GET.get('term')
            if term != None:

                clientes = [prod for prod in Cliente.objects.filter(nome_razao_social__icontains=term)]
            else:
                clientes = [prod for prod in Cliente.objects.all()]

            obj_list = [{'id': i.id, 'nome_razao_social': i.nome_razao_social} for i in clientes]

        else:
            return HttpResponse('Utilização incorreta.')
        
        return HttpResponse(json.dumps(obj_list), content_type='application/json')


class RefreshForm(View):

    def post(self, request, *args, **kwargs):
        obj_list = []
        transport = []
        clientes = Cliente.objects.all()

        if request.POST['pessoaId']:
            fazendas = Fazenda.objects.all().filter(pessoa_faz=request.POST['pessoaId'])
            enderecos = Endereco.objects.all().filter(pessoa_end=request.POST['pessoaId'])
        else:
            fazendas = False
            enderecos = False

        transportadoras = Transportadora.objects.all()
        
        cond_pag = CondicaoPagamento.objects.all()

        if clientes:
            obj_list += [pessoa.pessoa_ptr for pessoa in clientes]
        if fazendas:
            obj_list += [faz for faz in fazendas]
        if enderecos:
            obj_list += [end for end in enderecos]        
        if cond_pag:
            obj_list += [cond for cond in cond_pag]

        obj_list += [trans for trans in transportadoras]

        data = serializers.serialize('json', obj_list, fields=('id', 'descricao', 'nome', 'tipo_endereco','nome_razao_social'))
        
        return HttpResponse(data, content_type='application/json')