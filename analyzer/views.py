from django.shortcuts import render, redirect
from .forms import UploadStatementForm
from .models import Transaction
from django.db.models import Sum
import pandas as pd
import datetime
from decimal import Decimal

def convert_date_format(date_str):
    date_obj = datetime.datetime.strptime(date_str, '%d/%m/%y')
    return date_obj.strftime('%Y-%m-%d')

def detect_transaction_rows(df):
    transaction_rows = []
    transaction_data_started = False

    for index, row in df.iterrows():
        if transaction_data_started:
            if not pd.isna(row[0]) and isinstance(row[0], str) and row[1]:
                transaction_rows.append(index)
            else:
                break
        elif 'Date' in row.values and 'Narration' in row.values and 'Chq./Ref.No.' in row.values:
            transaction_data_started = True

    return transaction_rows



def upload_statement(request):
    if request.method == 'POST':
        form = UploadStatementForm(request.POST, request.FILES)
        if form.is_valid():
            print("valid")
            uploaded_file = request.FILES['statement_file']
            print("uploaded")
            if uploaded_file.name.endswith('.xls'):
                try:
                    print("verified")
                    statement_data = pd.read_excel(uploaded_file, header=None)

                    # Detect transaction rows
                    transaction_rows = detect_transaction_rows(statement_data)
                    
                    if transaction_rows:
                        start_row = min(transaction_rows)
                        end_row = max(transaction_rows)

                        transactions = []
                        for index, row in statement_data.iloc[start_row:end_row + 1].iterrows():
                            try:
                                if not pd.isna(row[0]) and isinstance(row[0], str):
                                    date_of_narration = convert_date_format(row[0])
                                    narration = row[1]
                                    refno = row[2]
                                    date_of_transaction = convert_date_format(row[3])
                                    withdrawal = row[4] if not pd.isna(row[4]) else 0
                                    deposit = row[5] if not pd.isna(row[5]) else 0
                                    balance = row[6]
                                    
                                    transaction = Transaction(
                                        date_of_narration=date_of_narration,
                                        narration=narration,
                                        refno=refno,
                                        date_of_transaction=date_of_transaction,
                                        widthdrawl=withdrawal,
                                        deposit=deposit,
                                        balance=balance
                                    )
                                    transactions.append(transaction)
                                else:
                                    print("Invalid date format or non-string value in 'Date' column.")
                            except Exception as e:
                                print(f"Error processing the file: {str(e)}")

                        Transaction.objects.bulk_create(transactions)

                        return redirect('query_transactions')
                    else:
                        print("No transaction rows found in the file.")
                except Exception as e:
                    print(f"Error processing the file: {str(e)}")
            else:
                return render(request, 'analyzer/dbms.html', {'form': form, 'error_message': 'Please upload an XLS file.'})
    else:
        form = UploadStatementForm()

    return render(request, 'analyzer/dbms.html', {'form': form})


def query_transactions(request):
    # transactions = Transaction.objects.all()
    top_deposits = Transaction.objects.filter(deposit__gt=0).order_by('-deposit')[:5]
    top_withdrawls = Transaction.objects.filter(widthdrawl__gt=0).order_by('-widthdrawl')[:5]
    deposit_sum = Transaction.objects.aggregate(total_deposits=Sum('deposit'))
    upi_transactions_count = Transaction.objects.filter(narration__icontains='upi').count()
    interest = Transaction.objects.filter(narration__icontains="CREDIT INTEREST CAPITALISED").aggregate(deposit=Sum('deposit'))
    dividend= Transaction.objects.filter(narration__icontains="ach c").aggregate(deposit=Sum('deposit'))
    return render(request, 'analyzer/query_transactions.html', {'top_deposits': top_deposits,'top_withdrawls':top_withdrawls,'income':deposit_sum,'upi':upi_transactions_count,
                                                                'interest':interest,'dividend':dividend})

def tax(request):
    deposit_sum = Transaction.objects.aggregate(total_deposits=Sum('deposit'))['total_deposits'] or Decimal('0')
    tax = [0, 0, 0, 0]

    if deposit_sum < 100000:
        tax[0] = Decimal('0')
        tax[1] = Decimal('0')
        tax[2] = Decimal('0')
        tax[3] = Decimal('0')
    elif deposit_sum < 300000:
        tax[0] = Decimal('0')
        tax[1] = Decimal('0.1') * (deposit_sum - Decimal('100000'))
        tax[2] = Decimal('0')
        tax[3] = Decimal('0')
    elif deposit_sum < 500000:
        tax[0] = Decimal('0')
        tax[1] = Decimal('0.1') * Decimal('200000')
        tax[2] = Decimal('0.2') * (deposit_sum - Decimal('300000'))
        tax[3] = Decimal('0')
    else:
        tax[0] = Decimal('0')
        tax[1] = Decimal('0.1') * Decimal('200000')
        tax[2] = Decimal('0.2') * Decimal('200000')
        tax[3] = Decimal('0.3') * (deposit_sum - Decimal('500000'))

    total_tax = sum(tax)

    return render(request, 'analyzer/tax.html', {
        'total_tax': total_tax,
        'tax0': tax[0],
        'tax1': tax[1],
        'tax2': tax[2],
        'tax3': tax[3]
    })
