from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.contrib.auth.decorators import login_required
from .models import Stock, Transaction, User, TransactionHistory

from .forms import LoginForm, RegisterForm

# Create your views here.
def index(request):
    return HttpResponse("HELLO WORLD!!")

# display all stocks present in the database
class StockList(View, LoginRequiredMixin):
    template = "backend/stock_list.html"

    def get(self, request):
        stocks = Stock.objects.all()
        return render(request, self.template, {
            'stocks': stocks,
        })

class login_view(View):
    template = "backend/login.html"
    success_url = "backend:StockList"

    def get(self, request):
        form = LoginForm()
        return render(request, self.template, {
            'form': form,
            'message': "Welcome!!, Please login to get access to all features",
        })

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            uname = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=uname, password=password)

            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse_lazy(self.success_url))
            else:
                return render(request, self.template, {
                    'form': LoginForm(),
                    'message': "Invalid username or password",
                })
        else:
            return render(request, self.template, {
                'form': LoginForm(),
                'message': "Please Enter all fields",
            })

@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("backend:register"))

class Register(View):
    template = 'backend/register.html'

    def get(self, request):
        form = RegisterForm()
        return render(request, self.template, {
            'form': form,
            'message': 'Please Enter Your UserName',
        })

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            uname = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            p1 = form.cleaned_data["password"]
            p2 = form.cleaned_data["confirm_password"]
            if not p1 == p2:
                return render(request, self.template, {
                    'form': RegisterForm(),
                    'message': "Passwords don't match",
                })
            try:
                user = User.objects.create_user(uname, first_name=first_name, last_name=last_name, email=email, password=p1)
                user.save()

            except IntegrityError:
                return render(request, self.template, {
                    'form': RegisterForm(),
                    'message': "An Account With This User Name Already Exists",
                })

            return HttpResponseRedirect(reverse("backend:StockList"))

# buy a particular stock and create a transaction
class BuyStock(View, LoginRequiredMixin):
    template = "backend/buy_stock.html"

    def get(self, request, stock_id):
        stock = Stock.objects.get(id=stock_id)
        # get stock price using stock.name and store in curr_price
        curr_price = 100
        return render(request, self.template, {
            'stock': stock,
            'price': curr_price,
        })

    # check if the stock id is present in user's transaction list
    def check_stock_id(self, stock_id):
        user = self.request.user
        transactions = user.transactions.all()
        for transaction in transactions:
            if transaction.stock.id == stock_id:
                return transaction
        return None

    def post(self, request, stock_id):
        stock = Stock.objects.get(id=stock_id)
        user = self.request.user
        transaction = self.check_stock_id(stock_id)
        intialQuant = 0
        if transaction is None:
            transaction = Transaction.objects.create(
                user=user,
                stock=stock,
                quantity=request.quantity,
                totalExpenditure=request.price*request.quantity,
            )
            intialQuant = 0
            transaction.save()
        else:
            intialQuant = transaction.quantity
            transaction.quantity += request.quantity
            transaction.totalExpenditure += request.price
            transaction.save()
        transactionHistory = TransactionHistory.objects.create(
            user = user.id,
            intialQuantity = intialQuant,
            finalQuantity = intialQuant + request.quantity,
            stockQuote = stock.name,
            priceAtWhichBought = request.price,
            intialCredits = user.credits,
            finalCredits = user.credits - request.price,
        )
        transactionHistory.save()
        user.credit -= request.price
        user.save()
        return HttpResponseRedirect(reverse("backend:stock_list"))

# sell a particular stock and update that particular stock transaction and increase the user credits and user profit
class SellStock(View, LoginRequiredMixin):
    template = "backend/sell_stock.html"

    def get(self, request, stock_id):
        stock = Stock.objects.get(id=stock_id)
        # get stock price using stock.name and store in curr_price
        curr_price = 100
        user = self.request.user
        transactions = user.transactions.all()
        for transaction in transactions:
            if transaction.stock.id == stock_id:
                return render(request, self.template, {
                    'stock': stock,
                    'transaction': transaction,
                    'price': curr_price,
                })

    # check if the stock id is present in user's transaction list
    def check_stock_id(self, stock_id):
        user = self.request.user
        transactions = user.transactions.all()
        for transaction in transactions:
            if transaction.stock.id == stock_id:
                return transaction
        return None

    def post(self, request, stock_id):
        stock = Stock.objects.get(id=stock_id)
        user = self.request.user
        transaction = self.check_stock_id(stock_id)
        if transaction is None:
            #show error that you don't have that stock
            return HttpResponseRedirect(reverse("backend:stock_list"))
        else:
            intialQuant = transaction.quantity
            transaction.quantity -= request.quantity
            # update user credits and profit
            user.credits += request.price
            user.profit += request.price
            transaction.save()
            transactionHistory = TransactionHistory.objects.create(
                user = user.id,
                intialQuantity = intialQuant,
                finalQuantity = intialQuant - request.quantity,
                stockQuote = stock.name,
                priceAtWhichSold = request.price,
                intialCredits = user.credits,
                finalCredits = user.credits + request.price*request.quantity,
            )
            transactionHistory.save()
            return HttpResponseRedirect(reverse("backend:stock_list"))

# display all transactions and stocks owned by a user and (TODO) its transactions
class UserDashBoard(View, LoginRequiredMixin):
    template = "backend/user_dashboard.html"

    def get_transaction_history(self, request, userID):
        allTransactions = TransactionHistory.objects.raw(
            'SELECT * FROM Transaction_History WHERE user = %s', [userID]
        )

    def get(self, request):
        user = self.request.user
        transactions = user.transactions.all()
        # for each transaction, get the stock details and store them together
        stocksAndTransactionDetails = []
        for transaction in transactions:
            stock = Stock.objects.get(id=transaction.stock.id)
            # adding stock and transaction as one object in stocksAndTransactionDetails
            stocksAndTransactionDetails.append({
                'stock': stock,
                'transaction': transaction,
            })

        allTransactionDetials = get_transaction_history(self, request, user.id)


        return render(request, self.template, {
            'portfolioDetails': stocksAndTransactionDetails,
            'allTransactionDetials': allTransactionDetials,
        })

# user public profile in which we show the user's credits, profit and its total stocks owned
class UserProfile(View):
    template = "backend/user_profile.html"

    def user_Public_Profile(self, request, userID):
        user = User.objects.get(id=userID)
        transactions = user.transactions.all()
        totalExpenditure = 0
        stockDetails = []
        for transaction in transactions:
            totalExpenditure += transaction.totalExpenditure
            stock = Stock.objects.get(id=transaction.stock.id)
            stockDetails.append({
                'name': stock.name,
                'description': stock.description,
                'quantityOwned': transaction.quantity,
            })

        userPortfolio = {
            'name' : user.username,
            'credits' : user.credits,
            'profit' : user.profit,
            'totalExpenditure' : totalExpenditure,
            'stockDetails' : stockDetails,
        }

        return render(request, self.template, {
            'userPortfolio': userPortfolio,
        })

# create a leaderboard in which display all the users and their profit in descending order of profit
class LeaderBoard(View):
    template = "backend/leaderboard.html"

    def get(self, request):
        users = User.objects.all()
        usersAndProfit = []
        for user in users:
            i = 1;
            usersAndProfit.append({
                'id': user.id,
                'rank': i,
                'name' : user.username,
                'profit' : user.profit,
                'credits' : user.credits,
            })
            i += 1
        usersAndProfit = sorted(usersAndProfit, key=lambda k: k['profit'], reverse=True)
        return render(request, self.template, {
            'usersAndProfit': usersAndProfit,
        })

@login_required
class AddFriend(View, LoginRequiredMixin):
# add a friend to a user
    template = "backend/add_friend.html"

    def post(self, request, userID):
        CurrentUser = self.request.user
        user = User.objects.get(id=userID)
        user.friends.add(request.user)
        CurrentUser.friends.add(user)
        CurrentUser.save()
        user.save()
        return HttpResponseRedirect(reverse("backend:user_profile", args=(userID,)))

# get all the transaction history of a particular user.
# @login_required
# class TransactionHistoryOfAUser(View):
#     template = "backend/transaction_history.html"

#     def get_transaction_history(self, request, userID):
#         allTransactions = TransactionHistory.objects.raw(
#             'SELECT * FROM Transaction_History WHERE user = %s', [userID]
#         )

#         return render(request, self.template, {
#             'allTransactionsDetails': allTransactions,
#         })
