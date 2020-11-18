from django.shortcuts import render

def element_list(request):
    elements = Element.objects.all().prefetch_related('element_factor')
    context = {'elements': elements,}
    return(render(request, 'element/element_list.html', context))
