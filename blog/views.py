from django.shortcuts import render, get_object_or_404
from .models import Post
from django.utils import timezone
from .forms import PostForm
from django.shortcuts import redirect
import json
from watson_developer_cloud import ToneAnalyzerV3
from watson_developer_cloud.tone_analyzer_v3 import ToneInput
from watson_developer_cloud import LanguageTranslatorV3


language_translator = LanguageTranslatorV3(
    version='2018-05-01',
    iam_apikey='gIoWznP7aImlRNV39HpCYPVpGRZVU33wJt0bu3gkAHSM',
    url='https://gateway.watsonplatform.net/language-translator/api')

service = ToneAnalyzerV3(
    # url is optional, and defaults to the URL below. Use the correct URL for your region.
    # url='https://gateway.watsonplatform.net/tone-analyzer/api',
    username='f1befa43-c74c-475b-aa85-a1a3d6514d7d',
    password='1NKDhU27oP5U',
    version='2018-05-01')


def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    names = []
    for post in posts:
        translation = language_translator.translate(
            text=post.text, model_id='en-ar').get_result()
        obj = (json.dumps(translation, indent=2, ensure_ascii=False))
        obj2 = json.loads(obj)
        post.obj2 = obj2['translations'][0]['translation']
        post.w_count = obj2['word_count']
        post.c_count = obj2['character_count']
        tone_input = post.text
        tone = service.tone(tone_input=tone_input, content_type="text/plain", sentances=False).get_result()
        tone2 = (json.dumps(tone, indent=2))
        tone3 = json.loads(tone2)
        post.i = len(tone3['document_tone']['tones'])
        if post.i == 1:
            post.tone_score1 = tone3['document_tone']['tones'][0]['score']
            post.tone_name1 = tone3['document_tone']['tones'][0]['tone_name']
        elif post.i > 1:
            post.tone_score1 = tone3['document_tone']['tones'][0]['score']
            post.tone_name1 = tone3['document_tone']['tones'][0]['tone_name']
            post.tone_score2 = tone3['document_tone']['tones'][1]['score']
            post.tone_name2 = tone3['document_tone']['tones'][1]['tone_name']
        else:
            post.tone_score1 = 'null'
            post.tone_name1 = 'null'
        print("Tone count:  " + str(post.i))
    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})


def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})


def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})
