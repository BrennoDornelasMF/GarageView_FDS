from django.shortcuts import render

from django.http import HttpResponse, Http404
from .models import Anuncio
from django.views import View
 
from django.shortcuts import redirect
from django.urls import reverse

class MainView(View):
    def get(self, request):
        anuncios = Anuncio.objects.order_by("-data_criacao")
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        try:
            if min_price:
                anuncios = anuncios.filter(preco__gte=min_price)
            if max_price:
                anuncios = anuncios.filter(preco__lte=max_price)
        except Exception:
            pass
        contexto = {'anuncios': anuncios, 'min_price': min_price or '', 'max_price': max_price or ''}
        return render(request, 'forum/index.html', contexto)


class AdDetailView(View):
    def get(self, request, ad_id):
        try:
            ad = Anuncio.objects.get(pk=ad_id)
        except Anuncio.DoesNotExist:
            raise Http404("Anúncio inexistente")
        contexto = {'ad': ad}
        return render(request, 'forum/ad_detail.html', contexto)


class CreateAdView(View):
    def get(self, request):
        return render(request, 'forum/create_ad.html')

    def post(self, request):
        titulo = request.POST.get('titulo')
        descricao = request.POST.get('descricao')
        preco = request.POST.get('preco') or 0
        imagem_url = request.POST.get('imagem_url')
        if request.user.is_authenticated:
            vendedor = request.user.username
        else:
            vendedor = request.POST.get('vendedor') or 'anônimo'

        ad = Anuncio(titulo=titulo, descricao=descricao, preco=preco, imagem_url=imagem_url, vendedor=vendedor)
        ad.save()
        if request.POST.get('next') == 'novo':
            return redirect(reverse('forum:ad_create'))
        return redirect(reverse('forum:ad_detail', args=[ad.id]))


class SellerAdsView(View):
    def get(self, request):
        if request.user.is_authenticated:
            vendedor = request.user.username
            anuncios = Anuncio.objects.filter(vendedor=vendedor).order_by('-data_criacao')
            return render(request, 'forum/seller_ads.html', {'anuncios': anuncios, 'vendedor': vendedor})
        else:
            return render(request, 'forum/seller_ads.html', {'anuncios': [], 'vendedor': None})


class EditAdView(View):
    def get(self, request, ad_id):
        try:
            ad = Anuncio.objects.get(pk=ad_id)
        except Anuncio.DoesNotExist:
            raise Http404("Anúncio inexistente")
        return render(request, 'forum/edit_ad.html', {'ad': ad})

    def post(self, request, ad_id):
        try:
            ad = Anuncio.objects.get(pk=ad_id)
        except Anuncio.DoesNotExist:
            raise Http404("Anúncio inexistente")
        ad.titulo = request.POST.get('titulo')
        ad.descricao = request.POST.get('descricao')
        ad.preco = request.POST.get('preco') or ad.preco
        ad.imagem_url = request.POST.get('imagem_url')
        ad.save()
        return redirect(reverse('forum:ad_detail', args=[ad.id]))


class DeleteAdView(View):
    def post(self, request, ad_id):
        try:
            ad = Anuncio.objects.get(pk=ad_id)
        except Anuncio.DoesNotExist:
            raise Http404("Anúncio inexistente")
        ad.delete()
        return redirect(reverse('forum:index'))
 

