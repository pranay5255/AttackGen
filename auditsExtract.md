{
  "id": "sofamon-H01-0001",
  "source": {"report":"Sofamon-security-review.pdf","protocol":"Sofamon","auditor":null,"date":null},
  "tags": {"severity":"High","finding_code":"H-01"},
  "title": "Rounding issue in price formula",
  "category":"math"/"access-control"/
  "text": {
    "description": "The price computation divides before scaling, zeroing terms and enabling underpricing under certain supply values."
  },
  "code": "```solidity\nreturn ((totalSupply * curveFactor) / (totalSupply - x) - ...);\n```" ,
  "fix": {
    "recommendation": "Reorder operations; scale numerators before division.",
    "affected_contracts": ["SofamonMarket"],
    "affected_functions": ["priceFor"]
  }
}
