import requests
import json

from base.models import ScripMaster

SCRIP_MASTER_URL = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"


def run():
    print("running script")
    try:
        print("making request")
        response = requests.get(SCRIP_MASTER_URL)
        scripMaster = json.loads(response.text)

        length = len(scripMaster)
        print("Total records : ", length)

        if length > 0:
            print("Deleting all the records")
            ScripMaster.objects.all().delete()
            print("Deleted all the records")

            l = 0
            for scrip in scripMaster:
                token = scrip["token"]
                symbol = scrip["symbol"]
                name = scrip["name"]
                instrumenttype = scrip["instrumenttype"]
                exch_seg = scrip["exch_seg"]

                try:
                    obj = ScripMaster.objects.create(token=token)
                    obj.symbol = symbol
                    obj.name = name
                    obj.instrumenttype = instrumenttype
                    obj.exch_seg = exch_seg
                    obj.save()
                except Exception as e:
                    print(e)

                l = l + 1
                print("completed : ", l)
        print("request completed")

    except Exception as e:
        print(e)

    print("script exiting")
