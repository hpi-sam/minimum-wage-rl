# Generated by Django 4.0.2 on 2022-05-18 12:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bank',
            fields=[
                ('liquid_capital', models.FloatField(default=0.0)),
                ('interest_rate', models.FloatField(default='0.01')),
                ('bank_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'bank',
            },
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('company_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('company_size_type', models.IntegerField()),
                ('hiring_rate', models.FloatField(default=0.02)),
                ('junior_hiring_ratio', models.IntegerField()),
                ('senior_hiring_ratio', models.IntegerField()),
                ('executive_hiring_ratio', models.IntegerField()),
                ('skill_improvement_rate', models.FloatField()),
                ('num_junior_openings', models.IntegerField()),
                ('num_senior_openings', models.IntegerField()),
                ('num_executive_openings', models.IntegerField()),
                ('junior_salary_offer', models.FloatField()),
                ('senior_salary_offer', models.FloatField()),
                ('executive_salary_offer', models.FloatField()),
                ('company_account_balance', models.FloatField(default=0.0)),
                ('company_age', models.IntegerField(default=0)),
                ('company_score', models.FloatField(default=0.0)),
                ('num_junior_workers', models.IntegerField(default=0)),
                ('num_senior_workers', models.IntegerField(default=0)),
                ('num_executive_workers', models.IntegerField(default=0)),
                ('avg_junior_salary', models.FloatField(default=0.0)),
                ('avg_senior_salary', models.FloatField(default=0.0)),
                ('avg_executive_salary', models.FloatField(default=0.0)),
                ('open_junior_pos', models.IntegerField(default=0)),
                ('open_senior_pos', models.IntegerField(default=0)),
                ('open_exec_pos', models.IntegerField(default=0)),
                ('loan_taken', models.BooleanField(default=False)),
                ('loan_amount', models.FloatField(default=0.0)),
                ('closed', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'company',
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('country_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('minimum_wage', models.FloatField(default=2.0)),
                ('product_price', models.FloatField(default=1.0)),
                ('quantity', models.IntegerField(default=0)),
                ('inflation', models.IntegerField(default=0.0)),
                ('year', models.IntegerField(default=1)),
                ('yearly_produced_value', models.FloatField(default=0.0)),
                ('num_small_companies', models.IntegerField(default=3)),
                ('num_medium_company', models.IntegerField(default=2)),
                ('num_large_company', models.IntegerField(default=1)),
                ('unemployment_rate', models.FloatField(default=100.0)),
                ('total_unemployed', models.IntegerField(default=0)),
                ('average_income', models.FloatField(default=0.0)),
                ('average_skill_level', models.FloatField(default=1.0)),
                ('average_balance', models.FloatField(default=0.0)),
                ('poverty_rate', models.FloatField(default=0.0)),
                ('total_jun_jobs', models.FloatField(default=0.0)),
                ('total_senior_jobs', models.FloatField(default=0.0)),
                ('total_executive_jobs', models.FloatField(default=0.0)),
                ('fixed_cash_printing', models.FloatField(default=500.0)),
                ('total_money_printed', models.FloatField(default=0.0)),
                ('population', models.IntegerField(default=0)),
                ('bank', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='economic_simulator.bank', unique=True)),
            ],
            options={
                'db_table': 'country',
            },
        ),
        migrations.CreateModel(
            name='Market',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.IntegerField(default=0)),
                ('year', models.IntegerField(default=0)),
                ('market_value_year', models.FloatField()),
                ('amount_of_new_citizens', models.IntegerField(default=0)),
                ('inflation_rate', models.FloatField(default='0.01')),
                ('product_price', models.FloatField(default='1')),
            ],
            options={
                'db_table': 'market',
            },
        ),
        migrations.CreateModel(
            name='Worker',
            fields=[
                ('worker_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('skill_level', models.FloatField(default=1.0)),
                ('worker_account_balance', models.FloatField(default=0)),
                ('salary', models.FloatField(default=0)),
                ('age', models.IntegerField()),
                ('is_employed', models.BooleanField(default=False)),
                ('has_company', models.BooleanField(default=False)),
                ('bought_essential_product', models.BooleanField(default=False)),
                ('buy_first_extra_product', models.BooleanField(default=False)),
                ('buy_second_extra_product', models.BooleanField(default=False)),
                ('retired', models.BooleanField(default=False)),
                ('worker_score', models.FloatField(default=0.0)),
                ('create_start_up', models.BooleanField(default=False)),
                ('start_up_score', models.FloatField(default=0.0)),
                ('skill_improvement_rate', models.FloatField(default=0.0)),
                ('country_of_residence', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='economic_simulator.country')),
                ('works_for_company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='economic_simulator.company')),
            ],
            options={
                'db_table': 'worker',
            },
        ),
        migrations.CreateModel(
            name='Metric',
            fields=[
                ('year', models.IntegerField()),
                ('metric_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('num_small_companies', models.IntegerField(default=0)),
                ('num_medium_companies', models.IntegerField(default=0)),
                ('num_large_companies', models.IntegerField(default=0)),
                ('total_filled_jun_pos', models.IntegerField(default=0)),
                ('total_filled_sen_pos', models.IntegerField(default=0)),
                ('total_filled_exec_pos', models.IntegerField(default=0)),
                ('unemployed_jun_pos', models.IntegerField(default=0)),
                ('unemployed_sen_pos', models.IntegerField(default=0)),
                ('unemployed_exec_pos', models.IntegerField(default=0)),
                ('average_jun_sal', models.FloatField(default=0.0)),
                ('average_sen_sal', models.FloatField(default=0.0)),
                ('average_exec_sal', models.FloatField(default=0.0)),
                ('average_sal', models.FloatField(default=0.0)),
                ('unemployment_rate', models.FloatField(default=0.0)),
                ('poverty_rate', models.FloatField(default=0.0)),
                ('population', models.IntegerField(default=0)),
                ('minimum_wage', models.FloatField(default=0.0)),
                ('inflation', models.FloatField()),
                ('inflation_rate', models.FloatField()),
                ('bank_account_balance', models.FloatField(default=0.0)),
                ('product_price', models.FloatField(default=0.0)),
                ('quantity', models.IntegerField(default=0)),
                ('country_of_residence', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='economic_simulator.country')),
            ],
            options={
                'db_table': 'metric',
            },
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_number', models.IntegerField(default=1)),
                ('game_ended', models.BooleanField(default=False)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'game_info',
            },
        ),
        migrations.AddField(
            model_name='country',
            name='game',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='economic_simulator.game'),
        ),
        migrations.AddField(
            model_name='country',
            name='market',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='economic_simulator.market', unique=True),
        ),
        migrations.AddField(
            model_name='country',
            name='player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='company',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='economic_simulator.country'),
        ),
    ]
