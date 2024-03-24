##import from others apps
from .serializers import AdminUserSerializer
from ..users.permissions import IsAdminOrPostOnly
from ..spacetly_chatbot.models import Message
from ..image_generator.models import Image_Gene

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.permissions import IsAdminUser

from django.utils import timezone
from django.db.models import Sum,Count
from django.db.models.functions import ExtractMonth
import calendar
from django.db.models import Func, CharField, Value
from datetime import datetime, timedelta
import random
from django.contrib.auth.password_validation import validate_password


from django.contrib.auth import get_user_model

User = get_user_model()

class UserDashViewSet(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        total_users = User.objects.count()
        today = timezone.now().date()
        visitors_today = User.objects.filter(last_login__date=today).count()
        
        online_threshold = timezone.now() - timezone.timedelta(minutes=5)
        
        # Query users who have logged in within the time window
        online_users = User.objects.filter(last_login__gte=online_threshold)
        
        # Count the number of online users
        online_users_count = online_users.count()
        return Response({'total_registered_users': total_users,
                         'visitors_today': visitors_today,
                         'online_users_count': online_users_count

                         }, status=status.HTTP_200_OK)


class LastUsersPagination(LimitOffsetPagination):
    """
    Pagination class for last messages.
    """
    default_limit = 10
    max_limit = 10

    def get_paginated_response(self, data):
        return Response({
            'count': self.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'first': self.get_first_link(),
            'last': self.get_last_link(),
            'results': data
        })

    def get_last_link(self):
        if not self.request:
            return None
        if not self.request.query_params.get('offset'):
            return None
        url = self.request.build_absolute_uri()
        offset = (self.count // self.limit) * self.limit
        if offset <= 0:
            return None
        return f'{url}?limit={self.limit}&offset={offset}'

    def get_first_link(self):
        if not self.request:
            return None
        url = self.request.build_absolute_uri()
        return f'{url}?limit={self.limit}&offset=0'

class UserManagementViewSet(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminUser]
    pagination_class = LastUsersPagination
    filter_backends = [DjangoFilterBackend, SearchFilter,OrderingFilter]

    search_fields = ['username', 'email', 'name', 'is_staff', 'is_active']
    filterset_fields = ['username', 'email', 'name', 'is_staff', 'is_active']
    ordering_fields = ['username', 'email', 'name', 'is_staff', 'is_active', 'date_joined', 'last_login']
class UserManagementInfoViewSet(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminUser]
    
    
    data = {
        "month": calendar.month_abbr[1:],
        "words_generated": [random.randint(0, 2500) for i in range(1, 13)],
        "images_generated": [random.randint(0, 15) for i in range(1, 13)],
    }
    
    words_images_generated_graph = []

    for i in range(12):
        month_data = {
            "images": data["images_generated"][i],
            "words": data["words_generated"][i],
            "month": data["month"][i],
        }
        words_images_generated_graph.append(month_data)
    
    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        data =         {
            "user_info": serializer.data,
            "user_genrated" : {
                "Words_Generated" : random.randint(0, 2500),
                "Images_Generated" : random.randint(0, 15),
            },
            "subscription":{
                "is_subscribed" : random.choice([True, False]),
                "subscription_type" : random.choice(["Free", "Basic", "Standard", "Premium"]),
                "subscription_price" : 0.00,
                #Total words available: 100 . Total prepaid words available 0.
                "total_words_available" : 100,
                "prepaid_words_available":0,
                "percentage": random.randint(0, 100),
            },
            "words_images_generated_graph": self.words_images_generated_graph,
            "transactions":[
                {
                    "order_id": "RxJFnhms8h",
                    "status": "Completed",
                    "plan_name": "Free",
                    "price": 100.0,
                    "Gateway": "PayPal",
                    "paid_on_date": "05 Mar 2024",
                    "paid_on_time": "03:18 AM",
                    "pricing_plan": "Monthly"
                },
                {
            "order_id": "RxJFnhms8h",
            "status": "Pending",
            "plan_name": "Premium",
            "price": 300.0,
            "Gateway": "PayPal",
            "paid_on_date": "05 Mar 2024",
            "paid_on_time": "03:18 AM",
            "pricing_plan": "Monthly"
                },                
            ]
            
        }

        return Response(data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if 'new_password' in request.data:
            new_password = request.data['new_password']
            confirm_new_password = request.data['confirm_new_password']
            
            if not (new_password == confirm_new_password):
                return Response({'new_password': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                validate_password(new_password, instance)
                instance.set_password(new_password)
                instance.save()
            except :
                return Response({'new_password': 'Password is not strong enough.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()
class WordCount(Func):
    function = 'regexp_split_to_array'
    template = "%(function)s(%(expressions)s, '\\s+')"
    output_field = CharField()

class AdminDashboardViewSet(generics.GenericAPIView):
    permission_classes = [IsAdminOrPostOnly]
    
    ########################################
    #______________total users______________
    ########################################
    def get_total_new_users(self, start_date, end_date):
        return User.objects.filter(date_joined__range=(start_date, end_date)).count()
    def get_new_users_info(self): 
        current_date = datetime.now().date()

        current_month_start = current_date.replace(day=1)
        current_month_end = current_date.replace(day=calendar.monthrange(current_date.year, current_date.month)[1])

        last_month_start = current_month_start - timedelta(days=current_month_start.day)
        last_month_end = current_month_start - timedelta(days=1)
        
        current_year_start = current_date.replace(month=1, day=1)
        current_year_end = current_date.replace(month=12, day=31)

        total_new_users_current_month = self.get_total_new_users(current_month_start, current_month_end)
        total_new_users_last_month = self.get_total_new_users(last_month_start, last_month_end)
        total_new_users_current_year = self.get_total_new_users(current_year_start, current_year_end)

        return {
                'total_new_users_current_month': total_new_users_current_month,
                'total_new_users_last_month': total_new_users_last_month,
                'total_new_users_current_year': total_new_users_current_year
            }

    ########################################
    ######____total subscribers________#####
    ########################################

    def get_total_new_subscribers(self, start_date, end_date):
        pass
    def get_total_new_subscribers_info(self):
        try:
            total_subscribers = self.get_total_new_subscribers(start_date, end_date)
        except:
            total_subscribers_current_month= 0
            total_subscribers_last_month= 0
            total_subscribers_current_year= 0

            return{
                "total_subscribers_current_month":total_subscribers_current_month,
                "total_subscribers_last_month":total_subscribers_last_month,
                "total_subscribers_current_year":total_subscribers_current_year,
                
            }            
     
    
    ########################################
    ######____total income________#####
    ########################################           
    def get_total_income(self, start_date, end_date):
        # Implement logic to calculate total income based on transactions within the date range
        pass
    def get_total_income_info(self):
        try:
            total_income = self.get_total_income(start_date, end_date)
        except:
            total_income_current_month= 1000.00
            total_income_last_month= 10000.00
            total_income_current_year= 100000.00

            return{
                "total_income_current_month":total_income_current_month,
                "total_income_last_month":total_income_last_month,
                "total_income_current_year":total_income_current_year,
            }            

    ########################################
    ######____total spending________#####
    ########################################
    def get_total_estimated_spending(self, start_date, end_date):
        # Implement logic to calculate total income based on transactions within the date range
        pass
    def get_total_estimated_spending_info(self):
        try:
            total_estimated_spending = self.get_total_estimated_spending(start_date, end_date)
        except:
            total_estimated_spending_current_month= 0
            total_estimated_spending_last_month= 0
            total_estimated_spending_current_year= 0

            return{
                "total_estimated_spending_current_month":total_estimated_spending_current_month,
                "total_estimated_spending_last_month":total_estimated_spending_last_month,
                "total_estimated_spending_current_year":total_estimated_spending_current_year,
            }            

    ########################################
    ######____total words________#####
    ########################################
    
    def get_total_words_generated(self, period):
        # Get current date
        current_date = datetime.now().date()

        # Define start and end dates based on the specified period
        if period == 'current_month':
            start_date = current_date.replace(day=1)
            end_date = current_date
        elif period == 'last_month':
            end_date = datetime(current_date.year, current_date.month, 1) - timedelta(days=1)
            start_date = datetime(end_date.year, end_date.month, 1)
        elif period == 'current_year':
            start_date = datetime(current_date.year, 1, 1)
            end_date = current_date

        # Query messages within the specified period
        messages = Message.objects.filter(created_at__range=[start_date, end_date])

        # Calculate total words
        total_words = messages.annotate(num_words=Count(WordCount('content'))).aggregate(total_words=Sum('num_words'))['total_words'] or 0

        return total_words
    def get_total_words_generated_info(self):
        try :
            current_month_words = self.get_total_words_generated('current_month')
            last_month_words = self.get_total_words_generated('last_month')
            current_year_words = self.get_total_words_generated('current_year')
            return {
                "total_words_generated_current_month": current_month_words,
                "total_words_generated_last_month": last_month_words,
                "total_words_generated_current_year": current_year_words,
            }
        except:
            total_words_generated_current_month= 0
            total_words_generated_last_month= 0
            total_words_generated_current_year= 0

            return{
                "total_words_generated_current_month":total_words_generated_current_month,
                "total_words_generated_last_month":total_words_generated_last_month,
                "total_words_generated_current_year":total_words_generated_current_year,
            }            

    ########################################
    ######____total images________#####
    ########################################

    def get_total_images_generated(self, period):
        # Get current date
        current_date = datetime.now().date()

        # Define start and end dates based on the specified period
        if period == 'current_month':
            start_date = current_date.replace(day=1)
            end_date = current_date
        elif period == 'last_month':
            end_date = datetime(current_date.year, current_date.month, 1) - timedelta(days=1)
            start_date = datetime(end_date.year, end_date.month, 1)
        elif period == 'current_year':
            start_date = datetime(current_date.year, 1, 1)
            end_date = current_date

        # count images in Image_Gene table
        total_images = len(Image_Gene.objects.filter(created_at__range=[start_date, end_date]))
                
        return total_images

    def get_total_images_generated_info(self):
        current_month_images = self.get_total_images_generated('current_month')
        last_month_images = self.get_total_images_generated('last_month')
        current_year_images = self.get_total_images_generated('current_year')
        return {
            "total_images_generated_current_month": current_month_images,
            "total_images_generated_last_month": last_month_images,
            "total_images_generated_current_year": current_year_images,
        }

    ########################################
    ######____total documents________#####
    ########################################
    
    def get_total_documents_generated(self, period):
        # Get current date
        current_date = datetime.now().date()
        
        # Define start and end dates based on the specified period
        if period == 'current_month':
            start_date = current_date.replace(day=1)
            end_date = current_date
        elif period == 'last_month':
            end_date = datetime(current_date.year, current_date.month, 1) - timedelta(days=1)
            start_date = datetime(end_date.year, end_date.month, 1)
        elif period == 'current_year':
            start_date = datetime(current_date.year, 1, 1)
            end_date = current_date
        
        # Query documents within the specified period
        # documents = Document_Gene.objects.filter(created_at__range=[start_date, end_date])
        # Use raw SQL to query all fields of
        # documents = Document_Gene.objects.raw("SELECT * FROM admin_dash_document_gene WHERE created_at BETWEEN %s AND %s", [start_date, end_date])
        
        # # Calculate total documents
        # total_documents = len(documents)
        
        # return total_documents
        
        return 10
    
    def get_total_documents_generated_info(self):
        current_month_documents = self.get_total_documents_generated('current_month')
        last_month_documents = self.get_total_documents_generated('last_month')
        current_year_documents = self.get_total_documents_generated('current_year')
        return {
            
            "total_documents_generated_current_month": current_month_documents,
            "total_documents_generated_last_month": last_month_documents,
            "total_documents_generated_current_year": current_year_documents,
            
        }
             
    ########################################
    ######____total transactions________#####
    ########################################
    def get_total_transactions(self, period):
        # Get current date
        current_date = datetime.now().date()
        # Query transactions within the specified period
        if period == 'current_month':
            start_date = current_date.replace(day=1)
            end_date = current_date
        elif period == 'last_month':
            end_date = datetime(current_date.year, current_date.month, 1) - timedelta(days=1)
            start_date = datetime(end_date.year, end_date.month, 1)
        elif period == 'current_year':
            start_date = datetime(current_date.year, 1, 1)
            end_date = current_date
        # # Calculate total transactions
        # transactions = Transaction.objects.filter(created_at__range=[start_date, end_date])
        # total_transactions = len(transactions)
        # return total_transactions

        return 30
    
    def get_total_transactions_info(self):
        current_month_transactions = self.get_total_transactions('current_month')
        last_month_transactions = self.get_total_transactions('last_month')
        current_year_transactions = self.get_total_transactions('current_year')
        return {
            
            "total_transactions_current_month": current_month_transactions,
            "total_transactions_last_month": last_month_transactions,
            "total_transactions_current_year": current_year_transactions,
        }
    
    ########################################
    ######____ New Users graph________#####
    ########################################
    def get_total_new_users_per_month(self):
        current_year = timezone.now().year
        user_data = User.objects.filter(date_joined__year=current_year) \
                                 .annotate(month=ExtractMonth('date_joined')) \
                                 .values('month') \
                                 .annotate(count=Count('id'))

        labels = [datetime.strptime(str(i), "%m").strftime("%b") for i in range(1, 13)]
        data = [0] * 12

        for entry in user_data:
            data[entry['month'] - 1] = entry['count']

        return {'labels': labels, 'data': data}
    
    #make Finance Overview with default values return labels , data for show it in graph 
    def get_finance_overview_per_month(self):
        return {'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], 
                'data': [100, 2000, 200, 50, 1000, 0, 0, 100, 0, 0, 0, 0]}
    
    #get Latest Registrations 
    def get_last_registrations(self):
        latest_registrations = User.objects.order_by('-date_joined')[:6]
        
        # Serialize user data into dictionaries
        serialized_users = []
        for user in latest_registrations:
            user_date_joined = user.date_joined
            formatted_date = user_date_joined.strftime("%d %b %Y")  # "YYYY Mon DD"
            formatted_time = user_date_joined.strftime("%I:%M %p")  # "HH:MM AM/PM"

            serialized_user = {
                'id': user.id,
                'profile_picture' : user.profile_picture.url,
                'username': user.username,
                'email' : user.email,
                'is_staff' : user.is_staff,
                'is_active' : user.is_active,
                'date': formatted_date,
                'time': formatted_time

            }
            serialized_users.append(serialized_user)
        
        return serialized_users
    
    #get latest transactions
    def get_last_transactions(self):
        # latest_transactions = Transaction.objects.order_by('-created_at')[:6]
        
        #return defulat date  Paid By ,Status ,Total,Gateway,Created i need order id = str
        return [
            {
            'order_id': 'RxJFnhms8h',
            'user_info' : {
                'profile_picture' : 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=387&q=80',
                'username' : 'ahmed mohamed',
                'email' : 'p8wH6@example.com',
            },
            'status' : 'Completed',
            'plan_name' : 'Free',
            'price': 100.00,
            'Gateway' : 'PayPal',
            'paid_on_date' :timezone.now().strftime("%d %b %Y"),
            'paid_on_time' :timezone.now().strftime("%I:%M %p"),
            'pricing_plan': 'Monthly',

        },
            {
            'order_id': 'RxJFnhms8h',
            'user_info' : {
                'profile_picture' : 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=387&q=80',
                'username' : 'kirolos adel',
                'email' : 'p8wH6@example.com',
            },
            'status' : 'Pending',
            'plan_name' : 'Premium',
            'price': 300.00,
            'Gateway' : 'PayPal',
            'paid_on_date' :timezone.now().strftime("%d %b %Y"),
            'paid_on_time' :timezone.now().strftime("%I:%M %p"),
            'pricing_plan': 'Monthly',

        },
            {
            'order_id': 'RxJFnhks8h',
            'user_info' : {
                'profile_picture' : 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=387&q=80',
                'username' : 'John Doe',
                'email' : 'p8wH6@example.com',
            },
            'status' : 'Cancelled',
            'plan_name' : 'Free',
            'price': 200.00,
            'Gateway' : 'PayPal',
            'paid_on_date' :timezone.now().strftime("%d %b %Y"),
            'paid_on_time' :timezone.now().strftime("%I:%M %p"),
            'pricing_plan': 'Monthly',

        },
                  {
            'order_id': 'RxJFnhms8h',
            'user_info' : {
                'profile_picture' : 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=387&q=80',
                'username' : 'ahmed mohamed',
                'email' : 'p8wH6@example.com',
            },
            'status' : 'Completed',
            'plan_name' : 'Free',
            'price': 100.00,
            'Gateway' : 'PayPal',
            'paid_on_date' :timezone.now().strftime("%d %b %Y"),
            'paid_on_time' :timezone.now().strftime("%I:%M %p"),
            'pricing_plan': 'Monthly',

        },
            {
            'order_id': 'RxJFnhms8h',
            'user_info' : {
                'profile_picture' : 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=387&q=80',
                'username' : 'kirolos adel',
                'email' : 'p8wH6@example.com',
            },
            'status' : 'Pending',
            'plan_name' : 'Premium',
            'price': 300.00,
            'Gateway' : 'PayPal',
            'paid_on_date' :timezone.now().strftime("%d %b %Y"),
            'paid_on_time' :timezone.now().strftime("%I:%M %p"),
            'pricing_plan': 'Monthly',

        },
            {
            'order_id': 'RxJFnhks8h',
            'user_info' : {
                'profile_picture' : 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=387&q=80',
                'username' : 'John Doe',
                'email' : 'p8wH6@example.com',
            },
            'status' : 'Cancelled',
            'plan_name' : 'Free',
            'price': 200.00,
            'Gateway' : 'PayPal',
            'paid_on_date' :timezone.now().strftime("%d %b %Y"),
            'paid_on_time' :timezone.now().strftime("%I:%M %p"),
            'pricing_plan': 'Monthly',

        }
            
        ]
    
    def get_total_new_users_per_days_in_current_month(self):
    # Get the current date and month
        current_date = timezone.now()
        current_year = current_date.year
        current_month = current_date.month

        # Find the first day of the current month
        first_day_of_month = current_date.replace(day=1)

        # Find the number of days in the current month
        num_days_in_month = (first_day_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        # Initialize lists to store labels (days) and data (number of new users)
        labels = []
        data = []

        # Iterate over each day in the current month
        for day in range(1, num_days_in_month.day + 1):
            # Filter users joined on the current day
            users_joined_on_day = User.objects.filter(
                date_joined__year=current_year,
                date_joined__month=current_month,
                date_joined__day=day
            )

            # Append the day as label and count of users as data
            labels.append(day)
            data.append(users_joined_on_day.count())

        return {'labels': labels, 'data': data}
    def get(self, request, *args, **kwargs):
        #card 1
        get_new_users_info = self.get_new_users_info()
        #card 2
        get_total_subscribers_info = self.get_total_new_subscribers_info()
        #card 3
        get_total_estimated_spending_info = self.get_total_estimated_spending_info()
        #card 4
        get_total_income_info = self.get_total_income_info()
        #card 5
        get_total_words_generated_info = self.get_total_words_generated_info()
        #card 6
        get_total_images_generated_info = self.get_total_images_generated_info()
        #card 7
        get_total_documents_generated_info = self.get_total_documents_generated_info()
        #card 8
        get_total_transactions_info = self.get_total_transactions_info()
        
        #graph 1
        get_finance_overview_per_month = self.get_finance_overview_per_month()            
        
        #graph 2
        total_new_users_per_month_data = self.get_total_new_users_per_month()

        #get latest registrations
        get_last_registrations = self.get_last_registrations()
        
        #get last transactions
        get_last_transactions = self.get_last_transactions()
        
        get_total_new_users_per_days_in_current_month = self.get_total_new_users_per_days_in_current_month()
        data = {
            'users': get_new_users_info ,
            'subscribers': get_total_subscribers_info ,
            'income': get_total_income_info ,
            'estimated_spending': get_total_estimated_spending_info ,
            'words_generated': get_total_words_generated_info ,
            'images_generated': get_total_images_generated_info ,
            'total_documents_generated': get_total_documents_generated_info ,
            'total_transactions' : get_total_transactions_info ,
            'finance_overview_graph': get_finance_overview_per_month,
            'total_new_users_graph': total_new_users_per_month_data,
            'latest_registrations': get_last_registrations,
            'latest_transactions': get_last_transactions,
            'total_new_users_per_days_in_current_month': get_total_new_users_per_days_in_current_month
            
        }

        return Response(data, status=status.HTTP_200_OK)


class TransactionViewSet(generics.ListAPIView):
    pagination_class = LastUsersPagination
    permission_classes = [IsAdminUser]

    
    def get_queryset(self):
        transactions = []
        #loop to display last 10 transactions
        for i in range(12):
            transactions.append(
                                {
                    'order_id' : 'RxJFnhms8h',
                    'user_info' : {
                        'id' : 1,
                        'profile_picture' : 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=387&q=80',
                        'username' : 'John Doe',
                        'email' : 'p8wH6@example.com',
                        'country': 'USA',
                    },
                    'status' : 'Completed',
                    'plan_name' : 'Free',
                    'words_included' : random.randint(100, 1000),
                    'price' : random.randint(200, 400),
                    'Gateway' : 'PayPal',
                    'paid_on_date' :timezone.now().strftime("%d %b %Y"),
                    'paid_on_time' :timezone.now().strftime("%I:%M %p"),
                    'pricing_plan': 'Monthly',
                    'payment_frequency': random.choice(['Prepaid', 'On-demand','Postpaid', 'Annual']),
                    
                },
            )
        return  transactions

    def get(self, request, *args, **kwargs):
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)
            if page is not None:
                return self.get_paginated_response(page)
            return Response(queryset)
        
        
#TransactionInfoViewSet
class TransactionInfoViewSet(generics.ListAPIView):
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return  {
                    'order_id' : 'RxJFnhms8h',
                    'user_info' : {
                        'id' : 1,
                        'username' : 'John Doe',
                        'email' : 'p8wH6@example.com',
                        'country': 'USA',
                    },
                    'status' : 'Completed',
                    'plan_name' : 'Free',
                    'words_included' : random.randint(100, 1000),
                    'price' : random.randint(200, 400),
                    'Gateway' : 'PayPal',
                    'paid_on_date' :timezone.now().strftime("%d %b %Y"),
                    'paid_on_time' :timezone.now().strftime("%I:%M %p"),
                    'pricing_plan': 'Monthly',
                    'payment_frequency': random.choice(['Prepaid', 'On-demand','Postpaid', 'Annual']),
                    
                }
    def get(self, request, *args, **kwargs):
            queryset = self.get_queryset()
            return Response(queryset)