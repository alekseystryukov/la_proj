TAG=latest
build:
	docker build -t alekseystryukov/la_pro:$(TAG) .
	docker push alekseystryukov/la_pro:$(TAG)

TAG=latest
build_front:
	docker build -t alekseystryukov/la_pro_front:$(TAG) ./frontend
	docker push alekseystryukov/la_pro_front:$(TAG)
