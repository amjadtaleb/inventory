# Generated by Django 5.1.1 on 2024-09-11 16:40

from django.db import migrations


drop_sql = """DROP VIEW IF EXISTS `order_details`;"""

create_sql = """
CREATE OR REPLACE VIEW `order_details` AS
    with `taxes_at_order_time` AS (
        SELECT
            DISTINCT `sales_categorytax`.*
        FROM `sales_purchaceorder`
        JOIN `sales_categorytax` ON (
            `sales_categorytax`.`valid_from` <= `sales_purchaceorder`.`created_at`
        )
    ), `recent_taxes_at_order_time` AS (
        SELECT *
        FROM `taxes_at_order_time`
        JOIN `sales_tax` ON (`sales_tax`.`reference` = `taxes_at_order_time`.`tax_id`)
        WHERE (
            (`category_id`, `valid_from`) IN (
                SELECT `category_id`, MAX(`valid_from`)
                FROM `taxes_at_order_time`
                GROUP BY `category_id`
            )
        )
    )
    SELECT
        `sales_purchaceorder`.*
        , `sales_orderarticle`.`article_id`
        , `inventory_article`.`reference` AS `article_reference`
        , `sales_orderarticle`.`quantity`
        , `inventory_pricedarticle`.`price`
        , `recent_taxes_at_order_time`.`value` AS `tax_value`
    FROM `sales_purchaceorder`
    JOIN `sales_orderarticle` ON (`sales_orderarticle`.`purchace_order_id` = `sales_purchaceorder`.`id`)
    JOIN `inventory_pricedarticle` ON (`inventory_pricedarticle`.`id` = `sales_orderarticle`.`article_id`)
    JOIN `inventory_article` ON (`inventory_article`.`id` = `sales_orderarticle`.`article_id`)
    JOIN `recent_taxes_at_order_time` ON (
        `recent_taxes_at_order_time`.`category_id` = `inventory_article`.`category_id`
    );
"""


class Migration(migrations.Migration):
    dependencies = [
        ("sales", "0002_alter_purchaceorder_reference"),
        ("inventory", "0004_taxes"),
    ]

    operations = [
        migrations.RunSQL(
            create_sql,
            reverse_sql=drop_sql,
        ),
    ]
