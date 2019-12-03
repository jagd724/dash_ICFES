#'style': 'transform: rotate(90deg) translateX(25%) translateY(75%)'
# 0: {'label': '0°C', 'style': {'color': '#77b0b1'}},
style = {'transform': 'rotate(90deg) translateX(25%) translateY(75%)'}
years = [i for i in range (2000, 2019)]
y_marks = {}
for year in years:
    y_marks[year] = {'label':str(year), 'style':style}
print(y_marks)