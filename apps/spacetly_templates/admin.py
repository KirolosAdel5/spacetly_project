from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from django import forms
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.forms.models import BaseInlineFormSet

from .models import (
    Category,
    Template,
    TemplateSpecification,
    TemplateSpecificationField,
    TemplateType,
    UserTemplate
)


class TemplateSpecification(admin.TabularInline):
    model = TemplateSpecification


@admin.register(TemplateType)
class Admin(admin.ModelAdmin):
    inlines = [
        TemplateSpecification 
    ]
    list_display  = ('name','is_active')


class CustomMPTTModelAdmin(MPTTModelAdmin):
    list_display = ('name', )
    list_filter = ('is_active', )
    search_fields = ('name', )


admin.site.register(Category, CustomMPTTModelAdmin)


class TemplateSpecificationFieldInlineFormset(BaseInlineFormSet):
    def clean(self):
        super().clean()
        has_primary = False
        for form in self.forms:
            if not form.cleaned_data.get('DELETE', False):
                if form.cleaned_data.get('is_primary', False):
                    if has_primary:
                        raise forms.ValidationError("Only one primary field is allowed.")
                    has_primary = True


class TemplateSpecificationFieldInline(admin.TabularInline):
    model = TemplateSpecificationField
    extra = 1
    formset = TemplateSpecificationFieldInlineFormset


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'template_type', 'created_by')
    list_filter = ('template_type', 'created_by')

    def get_inline_instances(self, request, obj=None):
        inline_instances = super().get_inline_instances(request, obj)
        if obj:
            # If editing existing object, include TemplateSpecificationFieldInline
            for inline in inline_instances:
                if isinstance(inline, TemplateSpecificationFieldInline):
                    return inline_instances
            inline_instances.append(TemplateSpecificationFieldInline(self.model, self.admin_site))
        else:
            # If creating new object, always include TemplateSpecificationFieldInline
            inline_instances.append(TemplateSpecificationFieldInline(self.model, self.admin_site))
        return inline_instances
@admin.register(UserTemplate)
class UserTemplateAdmin(admin.ModelAdmin):
    list_display = ('user', 'template', 'created_at')
    list_filter = ('user', 'template', 'created_at')
    search_fields = ('user__username', 'template__title', 'created_at')
    readonly_fields = ('created_at',)
