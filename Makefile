.PHONY: docs clean-docs test

docs:
	$(MAKE) -C docs html

clean-docs:
	$(MAKE) -C docs clean

test:
	python manage.py test openedx_auto_enroll
