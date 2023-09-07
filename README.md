mingdaoyun-Python-SDK
-----

针对mingdaoyun的API封装的Python-SDK包

如果你在寻找PHP版本的,请点击(https://github.com/Lany-w/mingdaoyun-php-sdk)

## Installing

```shell
$ pip install mingdaoyun-sdk
```

## Usage

    ```python
    from mingdaoyun_sdk import Mingdaoyun
    mingdaoyun = Mingdaoyun('your app id', 'your app sign','host')
    
    mingdaoyun.table("table_alias").set_view("view_id").where("state", "=", "生效中").sort("autoid", True).find(all=True)
    
    ```

## API

- table("table_alias/worksheetId")  设置表名
- set_view("view_id") 设置视图
- where("field", "operator", "value") 设置查询条件
    - operator:
        - contains
        - =
        - startWith
        - endWith
        - notContain
        - !=
        - None 或者 "is null"
        - not null
        - \>
        - \>=
        - <
        - <=
        - RCEq
        - RCNe
        - between
        - nBetween
        - DateEnum
        - NDateEnum
        - DateBetween
        - DateNBetween
    - value:  如果是 DateBetween ， DateNBetween 要传 maxValue 和 minValue
- find(rowid=None, pageSize=1000, pageIndex=1, all=False) 查询数据
    - rowid 查询单条数据
    - pageSize 每页条数
    - pageIndex 页码
    - all 是否查询所有
- add 添加数据
- batch_add 批量添加数据
- delete (rowid) 删除数据 rowid 为逗号拼接的字符串
- edit (rowid, controls) 编辑数据
- batch_edit (rowids, control) 批量编辑数据
- count() 统计数据

## License

MIT
