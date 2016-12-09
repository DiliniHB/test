from django.shortcuts import render
from django.http import HttpResponse
from settings.models import District, BdSessionKeys
from incidents.models import IncidentReport
from .models import BmfPubMf, BhsPlc, BhsComDiseases, BhsVi, BhsOi, BucOmarStructure
import json
import yaml
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.apps import apps
import collections
from datetime import datetime, date
from django.utils import timezone
from django.http import Http404
from django.core.serializers.json import DjangoJSONEncoder
from django.core import serializers
from django.http import JsonResponse


# render baseline health table
def bs_medical_facilities(request):
    districts = District.objects.all()
    context = {
        'districts': districts
    }
    return render(request, 'base_line/health_baseline_district.html', context)


# test method to save data to be integrated to API
def bs_save_baseline_pub_mf():
    baseline_pub_mf = BmfPubMf()
    baseline_pub_mf.type_pub_mf = 'Teaching Hospitals'

    baseline_pub_mf.save()


def bs_health_status(request):
    context = {
        'districts': District.objects.all()
    }
    return render(request, 'base_line/health_baseline_rdh.html', context)


@csrf_exempt
def bs_save_hs_data_mock(request):
    bs_data = (yaml.safe_load(request.body))
    #bs_table_hs_data = (yaml.safe_load(request.body))
    #bs_data = (yaml.safe_load('{"table_data":{"Table_1":{"BhsPlc":[{"male":5,"female":3,"children":5,"elderly":7}],"BhsComDiseases":[{"com_disease":"Diarrhea","male":5,"female":6,"children":7,"elderly":8},{"com_disease":"Dengue","male":5,"female":6,"children":7,"elderly":8}],"BhsVi":[{"vital_indicators":"Under-5 Mortality Rate","male":3,"female":3,"children":3,"elderly":3},{"vital_indicators":"Mortality Rate","male":3,"female":3,"children":3,"elderly":3}],"BhsOi":[{"other_indicators":"Crude Birth Rate","unit_measure":1},{"other_indicators":"Maternal Mortality Rate","unit_measure":""}]}}}'))

    bs_table_hs_data = bs_data['table_data']
    com_data = bs_data['com_data']

    #bs_hs_data = json.loads('{"BhsPlc":[{"popMl_1":"345","popFm_1":"","popChUnder12_1":"","popElOver60_1":""}],"BhsComDiseases":[{"diarrheaComDMl_1":"dfg","diarrheaComDFm_1":"","diarrheaComChildren_1":"","diarrheaComElderly_1":""},{"dengueComDMl_1":"","dengueComDFm_1":"","dengueComDChildren_1":"","dengueComDElderly_1":""},{"othEnrComDMl_1":"","othEnrComDFm_1":"","othEnrComDChildren_1":"","othEnrComDElderly_1":""}],"BhsVi":[{"under5MrtRateViMl_1":"dfgh","under5MrtRateViFm_1":"","under5MrtRateViChildren_1":"","under5MrtRateViElderly_1":""},{"mrtRateViMl_1":"","mrtRateViFm_1":"","mrtRateViChildren_1":"","mrtRateViElderly_1":""},{"othEnrViMl_1":"","othEnrViFm_1":"","othEnrViChildren_1":"","othEnrViElderly_1":""}],"BhsOi":[{"crudeBirthRateOi_1":"sdf","maternalMrtRateOi_1":"","othsEnrOi_1":""}]}')
    #bs_hs_data = (yaml.safe_load('{"Table_1":{"BhsPlc":[{"popMl_1":5,"popFm_1":3,"popChUnder12_1":5,"popElOver60_1":7}],"BhsComDiseases":[{"commonDisease":"Diarrhea","diarrheaComDMl_1":5,"diarrheaComDFm_1":6,"diarrheaComChildren_1":7,"diarrheaComElderly_1":8},{"commonDisease":"Dengue","dengueComDMl_1":8,"dengueComDFm_1":7,"dengueComDChildren_1":8,"dengueComDElderly_1":5},{"commonDisease":"Enumerate","othEnrComDMl_1":8,"othEnrComDFm_1":5,"othEnrComDChildren_1":9,"othEnrComDElderly_1":9}],"BhsVi":[{"vital_indicators":"Under-5 Mortality Rate","under5MrtRateViMl_1":3,"under5MrtRateViFm_1":3,"under5MrtRateViChildren_1":3,"under5MrtRateViElderly_1":3},{"vital_indicators":"Mortality Rate","mrtRateViMl_1":1,"mrtRateViFm_1":2,"mrtRateViChildren_1":2,"mrtRateViElderly_1":3},{"vital_indicators":"Enumerate","othEnrViMl_1":1,"othEnrViFm_1":1,"othEnrViChildren_1":1,"othEnrViElderly_1":1}],"BhsOi":[{"other_indicators":"Crude Birth Rate","crudeBirthRateOi_1":1},{"other_indicators":"Maternal Mortality Rate","maternalMrtRateOi_1":""},{"other_indicators":"Others","othsEnrOi_1":1}]}}'))

    for interface_table in bs_table_hs_data:
        print 'interface table', ' -->', interface_table, '\n'
        for db_table in bs_table_hs_data[interface_table]:

            print 'db table', ' -->', db_table, '\n'

            for row in bs_table_hs_data[interface_table][db_table]:

                model_class = apps.get_model('base_line', db_table)
                model_object = model_class()

                # assigning common properties to model objects
                model_object.created_date = timezone.now()
                model_object.lmd = timezone.now()
                model_object.district_id = com_data['district']

                print 'row', ' --> ', row, '\n', ' object '
                # for index, property in enumerate(row):
                for index, property in enumerate(sorted(row)):
                    #db_property = bs_hs_property_mapper[interface_table][db_table][index]
                    #setattr(model_object, db_property, row[property])
                    setattr(model_object, property, row[property])

                    print 'property ', ' --> ', property, ' db_property ', row[property], ' index ', '\n'
                    model_object.save()

    return HttpResponse(com_data['district'])

# saving base line data
@csrf_exempt
def bs_save_hs_data(request):
    bs_data = (yaml.safe_load(request.body))
    bs_table_hs_data = bs_data['table_data']
    com_data = bs_data['com_data']
    todate = timezone.now()
    is_edit = bs_data['is_edit']

    if not is_edit:

        try:
            for interface_table in bs_table_hs_data:
                print 'interface table', ' -->', interface_table, '\n'
                for db_table in bs_table_hs_data[interface_table]:

                    print 'db table', ' -->', db_table, '\n'

                    for row in bs_table_hs_data[interface_table][db_table]:

                        model_class = apps.get_model('base_line', db_table)
                        model_object = model_class()

                        # assigning common properties to model object
                        model_object.created_date = todate
                        model_object.lmd = todate
                        model_object.district_id = com_data['district']
                        model_object.bs_date = com_data['bs_date']

                        print 'row', ' --> ', row, '\n', ' object '

                        for property in row:
                            setattr(model_object, property, row[property])

                            print 'property ', ' --> ', property, ' db_property ', row[property], ' index ', '\n'
                            model_object.save()

            record_exist = BdSessionKeys.objects.filter(bs_date=com_data['bs_date'])
            if not record_exist:
                bdSession = BdSessionKeys(bs_date=com_data['bs_date'], date=todate, data_type='base_line')
                bdSession.save()

        except Exception as e:
            return HttpResponse(e)

    else:
        bs_save_edit_data(bs_table_hs_data, com_data)

    return HttpResponse('success')


'''@csrf_exempt
def bs_get_data(request):
    todate = timezone.now()
    incident = IncidentReport.objects.get(pk=1)
    incident_date = incident.reported_date_time

    dayofyear = int(date.today().strftime("%j"))

    datediff = '(DAYOFYEAR(date) - %d + 365) MOD 365' % (
        dayofyear
    )

    #datediff = 'LEAST(ABS(DAYOFYEAR(reported_date_time) - %d), ABS((366 - %d + DAYOFYEAR(reported_date_time))) MOD 366)' % (
    #    dayofyear, dayofyear
    #)


    #base_line_data = BdSessionKeys.objects.extra(select={'datediff': datediff}).order_by('datediff')
    bs_session = BdSessionKeys.objects.values('bs_date').latest('date')
    bs_date = bs_session['bs_date']
    bs_buc_oma_structure_data = BucOmarStructure.objects.filter(bs_date=bs_date).values('rural_hospital',
                                                                                        'particulars',
                                                                                        'divisional_hospital')

    bs_buc_oma_structure_data = BucOmarStructure.objects.filter(bs_date=bs_date)

    bs_bhs_com_disease_data = BhsComDiseases.objects.filter(bs_date=bs_date)

    bs_mtable_data = serializers.serialize('json',
                                           {'BucOmarStructure': 4,
                                            'BhsComDiseases': 3})

    bs_mtable_data = {'BucOmarStructure': serializers.serialize('json', bs_buc_oma_structure_data),
                     'BhsComDiseases': serializers.serialize('json', bs_bhs_com_disease_data)}

    #return HttpResponse((bs_mtable_data), content_type="application/json")
    return HttpResponse(
        json.dumps(bs_mtable_data),
        content_type='application/javascript; charset=utf8'
    )'''


@csrf_exempt
def bs_get_data(request):
    todate = timezone.now()
    incident = IncidentReport.objects.get(pk=1)
    incident_date = incident.reported_date_time
    data = (yaml.safe_load(request.body))
    db_tables = data['db_tables']

    bs_session = BdSessionKeys.objects.values('bs_date').latest('date')
    bs_date = bs_session['bs_date']

    bs_mtable_data = {}

    for db_table in db_tables:
        model_class = apps.get_model('base_line', db_table)
        bs_mtable_data[db_table] = serializers.serialize('json', model_class.objects.filter(bs_date=bs_date).order_by('id'))

    return HttpResponse(
        json.dumps(bs_mtable_data),
        content_type='application/javascript; charset=utf8'
    )


table_property_mapper = {
    'Table_1':
        {'BhsPlc': ['children', 'elderly', 'female', 'male'],
         'BhsComDiseases': ['com_disease', 'male', 'female', 'children', 'elderly'],
         'BhsVi': ['children', 'elderly', 'female', 'male', 'vital_indicators'],
         'BhsOi': ['unit_measure', 'other_indicators']
         }
}


@csrf_exempt
def bs_fetch_edit_data(request):

    bs_date = '12/2016'
    district = 2
    data = (yaml.safe_load(request.body))
    table_name = data['table_name']
    #table_name = 'Table_1'
    tables = table_property_mapper[table_name]

    bs_mtable_data = {table_name: {}}

    for table in tables:
        table_fields = tables[table]
        model_class = apps.get_model('base_line', table)
        bs_mtable_data[table_name][table] = list(model_class.objects.filter(bs_date=bs_date, district=district).\
        values(*table_fields))

    return HttpResponse(
        json.dumps(bs_mtable_data),
        content_type='application/javascript; charset=utf8'
    )


@csrf_exempt
def bs_save_edit_data():
    #district = com_data['district']
    #bs_date = com_data['bs_date']
    district = 2
    bs_date = '12/2016'

    table_data = (yaml.safe_load('{"table_data": {"Table_1":{"BhsComDiseases":[{"com_disease":"Diarrhea","male":90,"female":6,"children":7,"elderly":8},{"com_disease":"Dengue","male":5,"female":6,"children":7,"elderly":8}]}}}'))
    table_data = table_data['table_data']

    for interface_table in table_data:
        print 'interface table', ' -->', interface_table, '\n'
        for db_table in table_data[interface_table]:

            print 'db table', ' -->', db_table, '\n'

            for row in table_data[interface_table][db_table]:

                model_class = apps.get_model('base_line', db_table)
                model_object = model_class.objects.filter(bs_date=bs_date, district=district, com_disease=row['com_disease'])
                model_object.update(**row)

                print 'row', ' --> ', row, ' id ', model_object[0].id, '\n'





