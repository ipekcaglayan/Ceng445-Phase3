from django.db.models import Count
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import *
from .forms import *


class Login(View):
    def get(self, request):
        form = AuthenticationForm()
        # signup_form = UserCreationForm()
        return render(request, 'shared_photo_library/login.html', {'form': form})

    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        signup_form = UserCreationForm()
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            print("user  logged in")
            return redirect('shared_photo_library:my_profile')
        return render(request, 'shared_photo_library/login.html', {'form': form})


class SignUp(View):
    def get(self, request):
        form = UserCreationForm()
        return render(request, 'shared_photo_library/signup.html', {'form': form})

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('shared_photo_library:login')
        return render(request, 'shared_photo_library/signup.html', {'form': form})


class Home(View):
    def get(self, request):
        return render(request, 'shared_photo_library/home.html')


class UploadPhoto(LoginRequiredMixin, View):
    def post(self, request):
        new_photo = Photo.objects.create(added_by=request.user)
        form = AddPhoto(request.POST, request.FILES, instance=new_photo)
        if form.is_valid():
            form.save()
            new_photo.load_meta_data()
            return redirect('shared_photo_library:photos')

    def get(self, request):
        form = AddPhoto()
        return render(request, "shared_photo_library/upload_photo.html", {'form': form})


class MyProfile(View):
    def get(self, request):
        logged_in_user = request.user
        return render(request, 'shared_photo_library/my_profile.html',
                      {'user': logged_in_user})


class PhotoView(View):
    def get(self, request):
        logged_in_user = request.user
        photos = list(Photo.objects.filter(added_by=logged_in_user).order_by('-added_time'))
        photos = photo_tags_as_list(photos)
        shared_collections = list(Collection.objects.filter(shared_users=logged_in_user).values('id', 'collection_name'))
        users_collections = list(Collection.objects.filter(owner=logged_in_user).values('id', 'collection_name'))
        return render(request, 'shared_photo_library/photos.html',
                      {'user': logged_in_user, 'photos': photos, 'shared_collections': shared_collections,
                       'users_collections': users_collections})

    def post(self, request, **kwargs):
        data = request.POST.dict()
        print(data)
        ph_id = data['id']
        photo = Photo.objects.get(id=ph_id)

        if data.get('delete'):
            Photo.objects.get(id=ph_id).delete()
            return redirect('shared_photo_library:photos')

        if data.get('collections'):
            collections_ids = data['collections'].split(",")[1:]
            collections_ids = set(collections_ids)
            collections = {col.id: col for col in Collection.objects.all()}
            for col_id in collections_ids:
                col = collections[int(col_id)]
                col.add_photo_to_collection(photo)
            return redirect('shared_photo_library:photos')

        photo.add_location(data['location'])
        photo.add_tags(data['tags-list'])
        if data.get('col_id'):
            col_id = int(data['col_id'])
            return redirect('shared_photo_library:collection_detail', id=col_id)
        return redirect('shared_photo_library:photos')


class CollectionView(View):
    def get(self, request):
        form = CreateCollection()
        logged_in_user = request.user
        users_collections = list(Collection.objects.filter(owner=logged_in_user).annotate(photo_number=Count('photos')))
        shared_collections = list(Collection.objects.filter(shared_users=logged_in_user).annotate(photo_number=Count('photos')))
        collections = users_collections + shared_collections
        return render(request, 'shared_photo_library/collections.html',
                      {'user': logged_in_user, 'form': form, 'collections': collections,
                       'users_collections': users_collections, 'shared_collections': shared_collections})

    def post(self, request):
        new_col = Collection.objects.create(owner=request.user)
        form = CreateCollection(request.POST, instance=new_col)
        if form.is_valid():
            form.save()
            return redirect('shared_photo_library:collections')


class CollectionDetail(View):
    def get(self, request, **kwargs):
        col_id = int(kwargs['id'])
        col = Collection.objects.get(id=col_id)
        photos = col.photos.all().order_by('-added_time')
        photos = photo_tags_as_list(photos)
        view_form = CreateView()

        filter_tags = col.get_filter_tags()

        # if user wants to add a photo to the collection, he/she can select from  only his/her uploaded photos
        # to add to collection
        users_all_photos = list(Photo.objects.filter(added_by=request.user).order_by('-added_time'))

        # users that collection can be shared with
        not_shared_users = [user.username for user in User.objects.all().exclude(shared_collections=col)]

        # users that collection already shared with
        shared_users = {user.username: user for user in User.objects.filter(shared_collections=col)}

        return render(request, 'shared_photo_library/collection_detail.html',
                      {'user': request.user, 'col': col, 'photos': photos, 'users_all_photos': users_all_photos,
                       'not_shared_users': not_shared_users, 'shared_users': shared_users, 'view_form': view_form,
                       'filter_tags': list(filter_tags)})

    def post(self, request, **kwargs):
        col_id = int(kwargs['id'])
        col = Collection.objects.get(id=col_id)
        data = request.POST.dict()
        if data.get('remove'):  # form submitted to remove a photo from collection
            photo_id = int(data.get('photo_id'))
            col.remove_photo_from_collection(Photo.objects.get(id=photo_id))
        elif data.get('selected-photos'):
            selected_photos_ids = data['selected-photos'].split(',')[1:]
            col.add_photos_to_collection(selected_photos_ids)
        elif data.get('remove-selected-photos'):
            selected_photos_ids = data['remove-selected-photos'].split(',')[1:]
            col.remove_photos_from_collection(selected_photos_ids)

        elif data.get('unshare-with'):
            u_id = int(data.get('unshare-with'))
            user = User.objects.get(id=u_id)
            col.unshare_with(user)

        elif data.get('share-with'):
            username = data.get('share-with')
            user = User.objects.get(username=username)
            col.share_with(user)

        return redirect('shared_photo_library:collection_detail', id=col_id)


class Filter(View):
    def get(self, request):
        logged_in_user = request.user
        users_views = list(FilterView.objects.filter(owner=logged_in_user).annotate(photo_number=Count('photos')))
        shared_views = list(FilterView.objects.filter(shared_users=logged_in_user).annotate(photo_number=Count('photos')))
        views = users_views + shared_views
        return render(request, 'shared_photo_library/filter_views.html',
                      {'user': logged_in_user, 'users_views': users_views, 'shared_views': shared_views, 'views': views})

    def post(self, request):
        data = request.POST.dict()
        print(data)
        col_id = int(data.get('col_id'))
        col = Collection.objects.get(id=col_id)
        if data.pop('create'):
            view = FilterView(owner=request.user, collection=col)
            view.update_view(data)

            return redirect('shared_photo_library:view_detail', id=view.id)
        return redirect('shared_photo_library:views')


class FilterViewDetail(View):
    def get(self, request, **kwargs):
        logged_in_user = request.user
        view_id = int(kwargs['id'])
        view = FilterView.objects.get(id=view_id)
        photos = view.photos.all().order_by('-added_time')
        photos = photo_tags_as_list(photos)
        filter_tags = view.collection.get_filter_tags()

        # users that view can be shared with
        not_shared_users = [user.username for user in User.objects.all().exclude(shared_views=view)]

        # users that collection already shared with
        shared_users = {user.username: user for user in User.objects.filter(shared_views=view)}
        return render(request, 'shared_photo_library/filter_view_detail.html',
                      {'user': logged_in_user, 'photos': photos, 'view': view, 'filter_tags': filter_tags,
                       'not_shared_users': not_shared_users, 'shared_users': shared_users})

    def post(self, request, **kwargs):
        data = request.POST.dict()
        print(data)
        logged_in_user = request.user
        view_id = int(kwargs['id'])
        view = FilterView.objects.get(id=view_id)

        if data.get('share-with'):
            username = data.get('share-with')
            user = User.objects.get(username=username)
            view.share_with(user)

        elif data.get('unshare-with'):
            u_id = int(data.get('unshare-with'))
            user = User.objects.get(id=u_id)
            view.unshare_with(user)

        else:  # set filter form submitted to update view filters
            view.update_view(data)
        return redirect('shared_photo_library:view_detail', id=view_id)




