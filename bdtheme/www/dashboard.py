from __future__ import unicode_literals
import frappe
import json
import random
import locale
from datetime import *
from dateutil.relativedelta import *
from frappe.website.render import clear_cache
from frappe.utils import getdate, add_months

def get_context(context):
    """Count Sales Invoice by date"""
    get_sales_invoice = frappe.db.sql("""SELECT sum(total) AS 'total_si', posting_date from `tabSales Invoice` WHERE STATUS = 'paid' GROUP BY posting_date order by posting_date ASC""", as_dict=1)
    context.sales_invoice = []
    context.posting_date = []


    for j in range(len(get_sales_invoice)):
        context.posting_date.append(get_sales_invoice[j].posting_date.strftime('%d/%m/%Y'))
        context.sales_invoice.append(get_sales_invoice[j].total_si)

    """Count Purchase Invoice by date"""
    get_purchase_invoice = frappe.db.sql("""SELECT sum(total) AS 'total_pi', posting_date FROM `tabPurchase Invoice` WHERE STATUS = 'paid' GROUP BY posting_date ORDER BY posting_date ASC""", as_dict=1)
    context.purchase_invoice = []
    context.posting_date_pi = []


    for j in range(len(get_purchase_invoice)):
        context.posting_date_pi.append(get_purchase_invoice[j].posting_date.strftime('%d/%m/%Y'))
        context.purchase_invoice.append(get_purchase_invoice[j].total_pi)
        

    """Count Pendapatan by date"""
    # get_pendapatan = frappe.db.sql("""SELECT sum(credit) AS total_pendapatan, posting_date FROM `tabGL Entry` WHERE account = '4110.000 - Penjualan - RE' GROUP BY posting_date ORDER BY posting_date ASC""", as_dict=1)
    get_pendapatan = frappe.db.sql("""SELECT sum(debit-credit) AS total_pendapatan, posting_date, (select parent_account FROM `tabAccount` where name = account) AS account_parent FROM `tabGL Entry` where account in (select name from `tabAccount` where parent_account = '4100.000 - Penjualan Barang Dagangan - RE') GROUP BY posting_date ORDER BY posting_date ASC""", as_dict=1)

    
    context.total_pendapatan = []
    context.posting_date_pend = []

    for j in range(len(get_pendapatan)):
        context.posting_date_pend.append(get_pendapatan[j].posting_date.strftime('%d/%m/%Y'))
        context.total_pendapatan.append(get_pendapatan[j].total_pendapatan)
        
    
    """Count Customer by credit"""
    get_customer = frappe.db.sql("""SELECT sum(credit) AS total_annual, party AS customer FROM `tabGL Entry` WHERE party_type = 'Customer' AND voucher_type = 'Payment Entry' GROUP BY party ORDER BY sum(credit) DESC LIMIT 5""", as_dict=1)
    context.customer = []
    context.total_annual = []

    for j in range(len(get_customer)):
        context.customer.append(get_customer[j].customer)
        context.total_annual.append(get_customer[j].total_annual)

      
    """Count Kas by balance"""
    get_bank = frappe.db.sql("""SELECT SUM(debit - credit) AS total, account as account_type, (select parent_account FROM `tabAccount` where name = account) AS account_parent FROM `tabGL Entry` where account in (select name from `tabAccount` where parent_account = '1121.000 - Bank Rupiah - RE' || parent_account = '1113.000 - Investasi Jangka Pendek - RE' || parent_account= '1111.000 - Kas Rupiah - RE') AND fiscal_year = '2020' GROUP BY account ORDER BY SUM(debit - credit) DESC""", as_dict=1)
    get_bank_2019 = frappe.db.sql("""SELECT SUM(debit - credit) AS total, account as account_type, (select parent_account FROM `tabAccount` where name = account) AS account_parent FROM `tabGL Entry` where account in (select name from `tabAccount` where parent_account = '1121.000 - Bank Rupiah - RE' || parent_account = '1113.000 - Investasi Jangka Pendek - RE' || parent_account= '1111.000 - Kas Rupiah - RE') AND fiscal_year = '2019' GROUP BY account ORDER BY SUM(debit - credit) DESC""", as_dict=1)
    
    context.total_bank = []
    context.total_bank_2019 = []
    context.account_parent_bank = []
    tot_kas = 0
    tot_deposito = 0
    tot_bank = 0

    tot_kas_2019 = 0
    tot_bank_2019 = 0
    tot_deposito_2019 = 0
    for j in range(len(get_bank)):
        if get_bank[j].account_parent == '1111.000 - Kas Rupiah - RE':
            tot_kas = tot_kas + get_bank[j].total
        elif get_bank[j].account_parent == '1113.000 - Investasi Jangka Pendek - RE':
            tot_deposito = tot_deposito + get_bank[j].total
        else:
            tot_bank = tot_bank + get_bank[j].total
          

    for k in range(len(get_bank_2019)):
        if get_bank_2019[k].account_parent == '1111.000 - Kas Rupiah - RE' :
            tot_kas_2019 = tot_kas_2019 + get_bank_2019[k].total
        elif get_bank_2019[k].account_parent == '1113.000 - Investasi Jangka Pendek - RE' :
            tot_deposito_2019 = tot_deposito_2019 + get_bank_2019[k].total
        else:
           tot_bank_2019 = tot_bank_2019 + get_bank_2019[k].total
            

    context.account_parent_bank.append('1111.000 - Kas Rupiah - RE')
    context.total_bank.append(tot_kas)
    context.total_bank_2019.append(tot_kas_2019)

    context.account_parent_bank.append('1113.000 - Investasi Jangka Pendek - RE')
    context.total_bank.append(tot_deposito)
    context.total_bank_2019.append(tot_deposito_2019)

    context.account_parent_bank.append('1121.000 - Bank Rupiah - RE')
    context.total_bank.append(tot_bank)
    context.total_bank_2019.append(tot_bank_2019)
    


    """Count biaya beban atas pendapatan"""
    context.total_biaya = []
    context.account_parent = []   
    context.total_biaya_prev = []
    context.account_parent_prev = []   
    get_biaya = frappe.db.sql("""SELECT SUM(debit-credit) AS total_kas, account as account_type, (select parent_account FROM `tabAccount` where name = account) AS account_parent FROM `tabGL Entry` where account in (select name from `tabAccount` where parent_account = '5110.000 - Beban Penjualan - RE' || parent_account = '5510.000 - Beban Lain lain - RE' || parent_account = '5310.000 - Biaya Penyusutan - RE' || parent_account = '5120.000 - Biaya Gaji & Kesejahteraan Pegawai - RE' || parent_account = '5130.000 - Biaya Kantor & Gudang - RE' || parent_account = '5210.000 - Biaya Gaji & Kesejahteraan Pegawai Indirect - RE' || parent_account = '5220.000 - Biaya Operational Indirect - RE' || parent_account = '5230.000 - Biaya Kantor Indirect - RE' || parent_account = '5410.000 - Biaya Amortisasi - RE') AND MONTH(posting_date) = MONTH(CURRENT_DATE()) GROUP BY account ORDER BY SUM(debit - credit) DESC""", as_dict=1)    
    get_biaya_prev = frappe.db.sql("""SELECT SUM(debit-credit) AS total_kas, account as account_type, (select parent_account FROM `tabAccount` where name = account) AS account_parent FROM `tabGL Entry` where account in (select name from `tabAccount` where parent_account = '5110.000 - Beban Penjualan - RE' || parent_account = '5510.000 - Beban Lain lain - RE' || parent_account = '5310.000 - Biaya Penyusutan - RE' || parent_account = '5120.000 - Biaya Gaji & Kesejahteraan Pegawai - RE' || parent_account = '5130.000 - Biaya Kantor & Gudang - RE'|| parent_account = '5210.000 - Biaya Gaji & Kesejahteraan Pegawai Indirect - RE' || parent_account = '5220.000 - Biaya Operational Indirect - RE' || parent_account = '5230.000 - Biaya Kantor Indirect - RE' || parent_account = '5410.000 - Biaya Amortisasi - RE') AND MONTH(posting_date) = MONTH(CURRENT_DATE()) - 1 GROUP BY account ORDER BY SUM(debit - credit) DESC""", as_dict=1)    


    tot_penjualan = 0
    tot_gaji = 0
    tot_kantor = 0
    tot_gaji_ind = 0
    tot_operational = 0
    tot_kantor_ind = 0
    tot_penyusutan = 0
    tot_amortisasi = 0
    tot_lain_lain = 0

    tot_penjualan_prev = 0
    tot_gaji_prev = 0
    tot_kantor_prev = 0
    tot_gaji_ind_prev = 0
    tot_operational_prev = 0
    tot_kantor_ind_prev = 0
    tot_penyusutan_prev = 0
    tot_amortisasi_prev = 0
    tot_lain_lain_prev = 0

    for k in range(len(get_biaya_prev)):
        if get_biaya_prev[k].account_parent == '5110.000 - Beban Penjualan - RE':
            tot_penjualan_prev = tot_penjualan_prev + get_biaya_prev[k].total_kas
        elif get_biaya_prev[k].account_parent == '5120.000 - Biaya Gaji & Kesejahteraan Pegawai - RE' :
            tot_gaji_prev = tot_gaji_prev + get_biaya_prev[k].total_kas
        elif get_biaya_prev[k].account_parent == '5130.000 - Biaya Kantor & Gudang - RE' :
            tot_kantor_prev = tot_kantor_prev + get_biaya_prev[k].total_kas
        elif get_biaya_prev[k].account_parent == '5210.000 - Biaya Gaji & Kesejahteraan Pegawai Indirect - RE' :
            tot_gaji_ind_prev = tot_gaji_ind_prev + get_biaya_prev[k].total_kas
        elif get_biaya_prev[k].account_parent == '5220.000 - Biaya Operational Indirect - RE' :
            tot_operational_prev = tot_operational_prev + get_biaya_prev[k].total_kas
        elif get_biaya_prev[k].account_parent == '5230.000 - Biaya Kantor Indirect - RE' :
            tot_kantor_ind_prev = tot_kantor_ind_prev + get_biaya_prev[k].total_kas
        elif get_biaya_prev[k].account_parent == '5310.000 - Biaya Penyusutan - RE' :
            tot_penyusutan_prev = tot_penyusutan_prev + get_biaya_prev[k].total_kas
        elif get_biaya_prev[k].account_parent == '5410.000 - Biaya Amortisasi - RE' :
            tot_amortisasi_prev = tot_amortisasi_prev + get_biaya_prev[k].total_kas
        else:
            tot_lain_lain_prev = tot_lain_lain_prev + get_biaya_prev[k].total_kas
   
    context.account_parent_prev.append('5110.000 - Beban Penjualan - RE')
    context.total_biaya_prev.append(tot_penjualan_prev)

    context.account_parent_prev.append('5120.000 - Biaya Gaji & Kesejahteraan Pegawai - RE')
    context.total_biaya_prev.append(tot_gaji_prev)

    context.account_parent_prev.append('5130.000 - Biaya Kantor & Gudang - RE')
    context.total_biaya_prev.append(tot_kantor_prev)

    context.account_parent_prev.append('5210.000 - Biaya Gaji & Kesejahteraan Pegawai Indirect - RE')
    context.total_biaya_prev.append(tot_gaji_ind_prev)

    context.account_parent_prev.append('5220.000 - Biaya Operational Indirect - RE')
    context.total_biaya_prev.append(tot_operational_prev)

    context.account_parent_prev.append('5230.000 - Biaya Kantor Indirect - RE')
    context.total_biaya_prev.append(tot_kantor_ind_prev)

    context.account_parent_prev.append('5310.000 - Biaya Penyusutan - RE')
    context.total_biaya_prev.append(tot_penyusutan_prev)

    context.account_parent_prev.append('5410.000 - Biaya Amortisasi - RE')
    context.total_biaya_prev.append(tot_amortisasi_prev)

    context.account_parent_prev.append('5510.000 - Beban Lain lain - RE')
    context.total_biaya_prev.append(tot_lain_lain_prev)

    for j in range(len(get_biaya)):
        if get_biaya[j].account_parent == '5110.000 - Beban Penjualan - RE':
            tot_penjualan = tot_penjualan + get_biaya[j].total_kas
        elif get_biaya[j].account_parent == '5120.000 - Biaya Gaji & Kesejahteraan Pegawai - RE' :
            tot_gaji = tot_gaji + get_biaya[j].total_kas
        elif get_biaya[j].account_parent == '5130.000 - Biaya Kantor & Gudang - RE' :
            tot_kantor = tot_kantor + get_biaya[j].total_kas
        elif get_biaya[j].account_parent == '5210.000 - Biaya Gaji & Kesejahteraan Pegawai Indirect - RE' :
            tot_gaji_ind = tot_gaji_ind + get_biaya[j].total_kas
        elif get_biaya[j].account_parent == '5220.000 - Biaya Operational Indirect - RE' :
            tot_operational = tot_operational + get_biaya[j].total_kas
        elif get_biaya[j].account_parent == '5230.000 - Biaya Kantor Indirect - RE' :
            tot_kantor_ind = tot_kantor_ind + get_biaya[j].total_kas
        elif get_biaya[j].account_parent == '5310.000 - Biaya Penyusutan - RE' :
            tot_penyusutan = tot_penyusutan + get_biaya[j].total_kas
        elif get_biaya[j].account_parent == '5410.000 - Biaya Amortisasi - RE' :
            tot_amortisasi = tot_amortisasi + get_biaya[j].total_kas 
        else:
            tot_lain_lain = tot_lain_lain + get_biaya[j].total_kas

    context.account_parent.append('5110.000 - Beban Penjualan - RE')
    context.total_biaya.append(tot_penjualan)

    context.account_parent.append('5120.000 - Biaya Gaji & Kesejahteraan Pegawai - RE')
    context.total_biaya.append(tot_gaji)

    context.account_parent.append('5130.000 - Biaya Kantor & Gudang - RE')
    context.total_biaya.append(tot_kantor)

    context.account_parent.append('5210.000 - Biaya Gaji & Kesejahteraan Pegawai Indirect - RE')
    context.total_biaya.append(tot_gaji_ind)

    context.account_parent.append('5220.000 - Biaya Operational Indirect - RE')
    context.total_biaya.append(tot_operational)

    context.account_parent.append('5230.000 - Biaya Kantor Indirect - RE')
    context.total_biaya.append(tot_kantor_ind)

    context.account_parent.append('5310.000 - Biaya Penyusutan - RE')
    context.total_biaya.append(tot_penyusutan)

    context.account_parent.append('5410.000 - Biaya Amortisasi - RE')
    context.total_biaya.append(tot_amortisasi)

    context.account_parent.append('5510.000 - Beban Lain lain - RE')
    context.total_biaya.append(tot_lain_lain)




    """Count Employee by date joining"""
    get_employee = frappe.db.sql("""SELECT COUNT(name) AS jumlah_employee, date_of_joining FROM tabEmployee GROUP BY date_of_joining ORDER BY date_of_joining ASC;""", as_dict=1)
    context.employee = []
    context.date_of_joining = []


    for k in range(len(get_employee)):
        context.date_of_joining.append(get_employee[k].date_of_joining.strftime('%d/%m/%Y'))
        context.employee.append(get_employee[k].jumlah_employee)


    """pendapata vs beban"""
    get_pendapatan = frappe.db.sql("""SELECT sum(B.debit) as "Debit", sum(B.credit) as "Credit", (sum(B.debit) - sum(B.credit)) as "Net" FROM `tabAccount` A
                                    JOIN `tabGL Entry` B ON A.name = B.account
                                    WHERE A.root_type = 'Income' AND fiscal_year = '2020'""", as_dict = 1)

    get_beban = frappe.db.sql("""SELECT sum(B.debit) as "Debit", sum(B.credit) as "Credit", (sum(B.debit) - sum(B.credit)) as "Net" FROM `tabAccount` A
                            JOIN `tabGL Entry` B ON A.name = B.account
                            WHERE A.root_type = 'Expense' AND fiscal_year = '2020'""", as_dict = 1)

    get_pendapatan_2019 = frappe.db.sql("""SELECT sum(B.debit) as "Debit", sum(B.credit) as "Credit", (sum(B.debit) - sum(B.credit)) as "Net" FROM `tabAccount` A
                                    JOIN `tabGL Entry` B ON A.name = B.account
                                    WHERE A.root_type = 'Income' AND fiscal_year = '2019'""", as_dict = 1)

    get_beban_2019 = frappe.db.sql("""SELECT sum(B.debit) as "Debit", sum(B.credit) as "Credit", (sum(B.debit) - sum(B.credit)) as "Net" FROM `tabAccount` A
                            JOIN `tabGL Entry` B ON A.name = B.account
                            WHERE A.root_type = 'Expense' AND fiscal_year = '2019'""", as_dict = 1)

    context.pendapatan = []
    context.pendapatan_2019 = []
    context.beban = []
    context.beban_2019 = []
    context.tahun = []

    tot_pendapatan = 0
    tot_beban = 0
  

    tot_pendapatan_2019 = 0
    tot_beban_19 = 0
    
    for j in range(len(get_pendapatan)):
        tot_pendapatan = tot_pendapatan + get_pendapatan[j].Net
      

    for j in range(len(get_beban)):
        tot_beban = tot_beban + get_beban[j].Net

    context.pendapatan.append(tot_pendapatan )
    context.beban.append(tot_beban )


