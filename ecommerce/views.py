from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from .models import Product, ProductBasket, Order, Category, About, Comment
from .forms import CommentForm

# read pep8 documentation on how to write python code

# Create your views here.
def available_product(request):
  data={}
  product_list = Product.objects.filter(status=True)
  data['available'] = product_list
  return render(request, "available_product.html", context=data)

    #unavailable_poduct 
def unavailable_product(request):
  data={}
  product_list = Product.objects.filter(status=False)
  data['unavailable'] = product_list
  return render(request, "unavailable_product.html", context=data)

def product_detail(request, product_id):
  data={}
  #objects = model manager, get= queryes(unique value :id)
  product_list = Product.objects.get(id = product_id)
  comment_list = product_list.comment_set.all()
  # we assigned product into product_ list
  data['product'] = product_list
  data['comment'] = comment_list
  return render(request, "product_detail.html", context=data)

@login_required
def product_comment(request, slug):
  template_name = 'product_comment.html'
  post = get_object_or_404(Product, slug=slug)
  comments = post.comments.filter(active=True)
  new_comment = None
# Comment posted
  if request.method == 'POST':
      comment_form = CommentForm(data=request.POST)
      if comment_form.is_valid():
# Create Comment object but don&#39;t save to database yet
          new_comment = comment_form.save(commit=False)
# Assign the current post to the comment
          new_comment.product = Product
# Save the comment to the database
          new_comment.save()
  else:
       comment_form = CommentForm()
  return render(request, template_name, {'product': Product,
'comments': comments,
'new_comment':new_comment,
'comment_form': comment_form})

@login_required
def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    order_product, created= ProductBasket.objects.get_or_create(
      product=product,
      user=request.user,
      ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.product.filter(item__slug=product.slug).exists():
          order_product.quantity += 1
          order_product.save()
          messages.info(request, "This product quantity was updated.")
          return redirect("ecommerce:order-summary")
        else:
          order.product.add(order_product)
          messages.info(request, "This product was added to your cart.")
          return redirect("ecommerce:order-summary")
    else:
      ordered_date = timezone.now()
      order = Order.objects.create(
          user=request.user, ordered_date=ordered_date)
      order.product.add(order_product)
      messages.info(request, "This product was added to your cart.")
      return redirect("ecommerce:order-summary")

@login_required
def remove_from_cart (request, slug, Order):
    product = get_object_or_404(Product, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False) 
    
    if order_qs.exists():
        Order = order_qs[0]
        # check if the order item is in the order
        if Order.product.filter(product__slug=product.slug).exists():
            order_product = ProductBasket.objects.filter(
                product=product,
                user=request.user,
                ordered=False
            )[0]
            Order.product.remove(order_product)
            order_product.delete()
            messages.info(request, "This product was removed from your cart.")
            return redirect("ecommerce:order-summary")
        else:
            messages.info(request, "This product was not in your cart")
            return redirect("ecommerce:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("ecommerce:product", slug=slug)

@login_required
#all requests by non-authenticated users will be redirected to the login page or shown an http error.
class OrderSummaryView(LoginRequiredMixin):
# args passes variable number of non keyworded argument list and on which operation of the list can be preformed, kwargs makes the function flexible.
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")

def about_view(request):
    data = {}
    data["about_us"] = "e-commerce" 
    return render(request, "about.html", context=data)
 


