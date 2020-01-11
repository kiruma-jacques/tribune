from django.shortcuts import render, redirect
from .models import Article, NewsLetterRecipients, MoringaMerch
from .forms import NewsLetterForm, NewArticleForm
from .email import send_welcome_email
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
import datetime as dt
from django.contrib.auth.decorators import login_required
from .serializer import MerchSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .permissions import IsAdminReadOnly

def welcome (request):
    return render(request, 'welcome.html')

def past_days_news(request,past_date):
    try:
        # converts data from the url
        date=dt.datetime.strptime(past_date, '%Y-%m-%d').date()
    except ValueError:
        raise Http404()
        assert False

    if date == dt.date.today():
        return redirect (news_today)

    news = Article.days_news(date)
    return render(request, 'all-news/past-news.html', {"date":date, "news":news})
# main page view function
def news_today(request):
    date = dt.date.today()
    news = Article.todays_news()
    # sign up and welcome email form
    # if request.method == 'POST':
    #     form = NewsLetterForm(request.POST)
    #     # form validation
    #     if form.is_valid():
    #         name = form.cleaned_data['your_name']
    #         email = form.cleaned_data['email']
    #         recipient = NewsLetterRecipients(name = name, email = email)
    #         recipient.save()
    #         send_welcome_email(name, email)
    #         HttpResponseRedirect('news_today')
    #
    # else:
    form = NewsLetterForm()
    return render(request, 'all-news/today-news.html', {"date":date, "news":news, "letterForm":form})

def search_results(request):
    if 'article' in request.GET and request.GET["article"]:
        search_term = request.GET.get("article")
        searched_articles = Article.search_by_title(search_term)
        message = f"{search_term}"
        return render(request, 'all-news/search.html', {"message":message, "articles":searched_articles})
    else:
        message = "You haven't searched for any term"
        return render (request, 'all-news/search.html',{"message":message})

@login_required(login_url='/accounts/login/')
def article(request, article_id):
    try:
        article = Article.objects.get(id = article_id)
    except DoesNotExist:
        raise Http404()
        return render(request, "all-news/article.html", {"article":article})

@login_required(login_url='/accounts/login/')
def new_article(request):
    if request.method == 'POST':
        form = NewArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.editor = request.user
            article.save()
        return redirect('newsToday')
    else:
        form = NewArticleForm()
    return render (request, 'new_article.html', {"form":form})

def newsletter(request):
    name = request.POST.get('your_name')
    email = request.POST.get('email')
    recipient = NewsLetterRecipients(name=name, email=email)
    recipient.save()
    send_welcome_email(name, email)
    data = {'success':'You have been successfully added to mailing list'}
    return JsonResponse(data)

class MerchList(APIView):
    def get(self, request, format=None):
        all_merch = MoringaMerch.objects.all()
        serializer = MerchSerializer(all_merch, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializers = MerchSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    permission_classes = (IsAdminReadOnly,)

class MerchDescription(APIView):
    permission_classes = (IsAdminReadOnly,)
    def get_merch(self, pk):
        try:
            return MoringaMerch.objects.get(pk=pk)
        except MoringaMerch.DoesNotExist:
            return Http404

    def get(self, request, pk, format=None):
        merch=self.get_merch(pk)
        serializers=MerchSerializer(merch)
        return Response(serializers.data)

    def put(self,request,pk,format=None):
        merch = self.get_merch(pk)
        serializers=MerchSerializer(merch,request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data)
        else:
            return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,pk,format=None):
        merch=self.get_merch(pk)
        merch.delete()
        return Response(status=status.HTTP_201_NO_CONTENT)
        
