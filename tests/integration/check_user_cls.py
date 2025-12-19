from src.registration_service.users.user import User

user1: User = User.create_user(username='kamalsai', firstname='kamal', lastname='sai', email='kamalsaidevarapalli@gmail.com', pwd='123456')
print(user1)

# user1_response: User = User.generate_success_response()
# print(user1_response)
