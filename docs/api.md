# API 3B GEO


## Description
API for manage places and retrieve data of scans filter by coordinates and dates


## Authorization
* Add header `Authorization` with value `Api-Key {{ api_key }}`


### Points definition
```
point1  __________________  point2
       |                  |
       |                  |
       |                  |
point3 |__________________| point4
```


## Endpoints

### Scans list
* `GET /api/scans`

#### Filter results with queryparams
* `point1` | required | value > `latitude,longitude`
* `point2` | required | value > `latitude,longitude`
* `point3` | required | value > `latitude,longitude`
* `point4` | required | value > `latitude,longitude`
* `range` | optional | value > `YYYY-MM-DD,YYYY-MM-DD`
* `date` | optional | value > `YYYY-MM-DD`
* `status` | optional | value > `validated | rejected | pending`
* `photo` | optional | value > `yes | no`
* `price` | optional | value > `normal | special`
* `brandtype` | optional | value > `mc | mp`
* `brands` | optional | value > `brand1,brand2,brand3`
* `groups` | optional | value > `group1,group2,group3`
* `lines` | optional | value > `line1,line2,line3`
* `stores` | optional | value > `store1,store2,store3`
* `units` | optional | value > `unit1,unit2,unit3`
* `search` | optional | value > `text search (product name or barcode)`
* `order` | optional | value > `asc | desc`

#### Response sample
```
{
    "data": [
        {
            "barcode": "10000000000",
            "brandName": "Brand name",
            "captureDate": "2020-08-03 12:10:11",
            "groupName": "(02) Seeds",
            "lineName": "Line",
            "id": 1,
            "isValid": 1,
            "price": "35.00",
            "productBarcode": "/path/image.png",
            "productMaxPrice": "0.00",
            "productMinPrice": "0.00",
            "productName": "Product name",
            "productPhoto": "/path/image.png",
            "productPicture": "/path/image.png",
            "productType": "MC",
            "productUnitQuantity": "5.00",
            "shelfPicture": "/path/image.png",
            "storeAddress": "Store address",
            "storeName": "Store name",
            "unitPrice": "0.00",
            "capturist": "Luis Romo",
            "validator": "Jonathan Rodriguez",
            "productCreation": "202105-30 22:25:00",
            "specialPrice": 1,
            "idStore": 1
        },
    ],
    "results": 1
}

```


### Places list
* `GET /api/places`

#### Response sample
```
{
    "data": [
        {
            "id": 1,
            "name": "Place name",
            "point1": "18.89873471,-99.18817521",
            "point2": "18.89873472,-99.18817522",
            "point3": "18.89873473,-99.18817523",
            "point4": "18.89873474,-99.18817524",
            "created_at": "2020-09-06T12:00:00",
            "updated_at": "2020-09-06T12:00:00"
        },
    ],
    "results": 1
}
```


### Places retrieve
* `GET /api/places/{{pk}}`

#### Response sample
```
{
    "id": 1,
    "name": "Place name",
    "point1": "18.89873471,-99.18817521",
    "point2": "18.89873472,-99.18817522",
    "point3": "18.89873473,-99.18817523",
    "point4": "18.89873474,-99.18817524",
    "created_at": "2020-09-06T12:00:00",
    "updated_at": "2020-09-06T12:00:00"
}
```


### Places creation
* `POST /api/places`

#### Data
* `point1` | required | value > `latitude,longitude`
* `point2` | required | value > `latitude,longitude`
* `point3` | required | value > `latitude,longitude`
* `point4` | required | value > `latitude,longitude`
* `name` | required | value > `string`

#### Response sample
```
{
    "id": 1,
    "name": "Place name",
    "point1": "18.89873471,-99.18817521",
    "point2": "18.89873472,-99.18817522",
    "point3": "18.89873473,-99.18817523",
    "point4": "18.89873474,-99.18817524",
    "created_at": "2020-09-06T12:00:00",
    "updated_at": "2020-09-06T12:00:00"
}
```


### Places update
* `PATCH /api/places/{{pk}}`

#### Data
* `point1` | optional | value > `latitude,longitude`
* `point2` | optional | value > `latitude,longitude`
* `point3` | optional | value > `latitude,longitude`
* `point4` | optional | value > `latitude,longitude`
* `name` | optional | value > `string`

#### Response sample
```
{
    "id": 1,
    "name": "Place name",
    "point1": "18.89873471,-99.18817521",
    "point2": "18.89873472,-99.18817522",
    "point3": "18.89873473,-99.18817523",
    "point4": "18.89873474,-99.18817524",
    "created_at": "2020-09-06T12:00:00",
    "updated_at": "2020-09-06T12:00:00"
}
```


### Places delete
* `DELETE /api/places/{{pk}}`

#### Response
Empty response with 204 status code
