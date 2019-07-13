from .models import Subscription
import stripe
from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse
from django.contrib.auth.models import User

def premium_required(function):
    def wrap(request, *args, **kwargs):
        
        if request.user.profile.is_premium:
            customer_stripe_id = Subscription.objects.filter(user_id=request.user).first()
            customer = stripe.Customer.retrieve(customer_stripe_id.customer_id)
            for sub in customer.subscriptions:
                # If subscription is active or unpaid/cancelled but not yet inactive
                if sub.status == 'active' or sub.status == 'trialing' or sub.status == 'incomplete' or sub.status == 'past_due' or sub.status == 'canceled':
                    return function(request, *args, **kwargs)
            
            current_user = User.objects.get(pk=request.user.id)
            current_user.is_premium = False
            current_user.save()
            print(current_user.is_premium)
            return redirect(reverse('subscribe'))
        else:
            if request.is_ajax():
                data = {}
                data['redirect'] = '/subscribe'
                return JsonResponse(data)
            return redirect(reverse('subscribe'))
            
    # wrap.__doc__ = function.__doc__
    # wrap.__name__ = function.__name__
    return wrap
    

    
    