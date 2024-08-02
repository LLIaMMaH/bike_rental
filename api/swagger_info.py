# -*- coding: utf-8 -*-

from drf_yasg.inspectors import SwaggerAutoSchema


class CustomAutoSchema(SwaggerAutoSchema):
    def get_operation(self, operation_keys=None):
        operation = super().get_operation(operation_keys)
        return operation


class BikeSchema(CustomAutoSchema):
    def get_operation(self, operation_keys=None):
        operation = super().get_operation(operation_keys)
        operation.summary = "Получение списка доступных велосипедов"
        operation.description = "Возвращает список велосипедов, доступных для аренды"
        return operation
