from django.db import migrations, models
import django.db.models.deletion


def forwards_copy_fk_to_m2m(apps, schema_editor):
    Product = apps.get_model('core', 'Product')
    Tags = apps.get_model('core', 'Tags')
    # get through model for the temporary m2m field
    through = Product._meta.get_field('tags_new').remote_field.through

    # For each product, if an FK existed in the old column 'tags_id', copy it
    for p in Product.objects.all().iterator():
        old_tag_id = getattr(p, 'tags_id', None)
        if old_tag_id:
            try:
                tag = Tags.objects.get(pk=old_tag_id)
            except Tags.DoesNotExist:
                continue
            through.objects.create(product_id=p.pk, tags_id=tag.pk)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_cartorderitems_product'),
    ]

    operations = [
        # Add missing fields to Tags model
        migrations.AddField(
            model_name='tags',
            name='name',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tags',
            name='slug',
            field=models.SlugField(default='', max_length=60, blank=True),
            preserve_default=False,
        ),

        # Add a temporary ManyToManyField on Product to hold migrated data
        migrations.AddField(
            model_name='product',
            name='tags_new',
            field=models.ManyToManyField(blank=True, to='core.Tags'),
        ),

        # Copy existing FK -> M2M associations (if any)
        migrations.RunPython(forwards_copy_fk_to_m2m, reverse_code=migrations.RunPython.noop),

        # Remove the old FK field 'tags' on Product
        migrations.RemoveField(
            model_name='product',
            name='tags',
        ),

        # Rename the temporary m2m field to the canonical name 'tags'
        migrations.RenameField(
            model_name='product',
            old_name='tags_new',
            new_name='tags',
        ),

        # Note: uniqueness constraints for Tags.name/slug are not applied here
        # to avoid index/name conflicts in environments where those indexes
        # may already exist. Add a separate migration to enforce uniqueness
        # after manual verification if desired.
    ]
