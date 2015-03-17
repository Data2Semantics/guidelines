How to use
==========

Server
------

```prolog
$ swipl metis.pl
```

Client
------

```bash
$ curl "http://localhost:3030/?guideline=http://guidelines.data2semantics.org/data/CIG-DM"
{
  "recommendations": [
    [
      "AlternativeActions",
      [
	"http://guidelines.data2semantics.org/data/RecDM-AntiThrombotic1",
	"http://guidelines.data2semantics.org/data/RecDM-AntiThrombotic2"
      ]
    ]
  ]
}
```

