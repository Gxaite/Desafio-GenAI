{#
  Usa o schema custom (+schema no dbt_project.yml) exatamente como escrito — sem prefixar
  com o schema do target. Assim os models caem em `silver` e `gold`, não `gold_silver`.
#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
