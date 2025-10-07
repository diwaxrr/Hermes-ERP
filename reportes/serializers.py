from rest_framework import serializers
from .models import ReporteConfiguracion

class ReporteConfiguracionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReporteConfiguracion
        fields = '__all__'