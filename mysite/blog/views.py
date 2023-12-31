from django.shortcuts import render
from .models import Post
# Create your views here.
from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail
from .forms import EmailPostForm,CommentForm

from django.core.paginator import Paginator, EmptyPage,\
 PageNotAnInteger
def post_list(request):
 object_list = Post.objects.all()
 tag=None

 if tag_slug:
     tag=get_object_or_404(Tag,slug=tag_slug)
     object_list=object_list.filter(tags__in=[tag])
 paginator = Paginator(object_list, 1) # 3 posts in each page
 page = request.GET.get('page')
 try:
    posts = paginator.page(page)
 except PageNotAnInteger:
 # If page is not an integer deliver the first page
    posts = paginator.page(1)
 except EmptyPage:
    # If page is out of range deliver last page of results
    posts = paginator.page(paginator.num_pages)
 return render(request,'blog/post/list.html',{'page': page,'posts': posts})

def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                                   status='published',
                                   publish__year=year,
                                   publish__month=month,
                                   publish__day=day)

    # List of active comments for this post
    comments=post.comments.filter(active=True)
    new_comment=None
    if request.method=='POST' :
        comment_form=CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment=comment_form.save(commit=False)
            new_comment.post=post
            new_comment.save()
    else :
        comment_form=CommentForm()
    return render(request,
        'blog/post/detail.html',
        {'post' : post,
         'comments' : comments,
         'new_comment' : new_comment,
         'comment_form' : comment_form})




def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                      f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message,'dev2@scube.net.in' , [cd['to']])
            sent = True

    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form,
                                                    'sent': sent})