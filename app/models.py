from sqlalchemy import (
    Column, Integer, String, ForeignKey, Float, DateTime, Table, Text, Boolean
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

# Таблица для связи многие-ко-многим между Users и Items для избранного
favorites_table = Table(
    'favorites',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('item_id', Integer, ForeignKey('items.id'), nullable=False)
)

# Таблица для связи многие-ко-многим между Users и Items для корзины
class Cart(Base):
    __tablename__ = 'cart'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    checkout_timestamp = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="cart_items")
    item = relationship("Item", back_populates="cart_entries")

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'item_id': self.item_id,
            'quantity': self.quantity,
            'created_at': self.created_at,
            'checkout_timestamp': self.checkout_timestamp
        }

# Таблица пользователей
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=True)
    avatar_url = Column(String, nullable=True)
    user_telegram_id = Column(Integer, unique=True, nullable=False)

    favorites = relationship("Item", secondary=favorites_table, back_populates="favorited_by")
    cart_items = relationship("Cart", back_populates="user")

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'username': self.username,
            'avatar_url': self.avatar_url,
            'user_telegram_id': self.user_telegram_id
        }

# Таблица альбомов
class Album(Base):
    __tablename__ = 'albums'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    display_order = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    is_available_to_order = Column(Boolean, default=True)
    is_visible = Column(Boolean, default=True)

    items = relationship("Item", back_populates="album")

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'display_order': self.display_order,
            'notes': self.notes,
            'is_available_to_order': self.is_available_to_order,
            'is_visible': self.is_visible
        }

# Таблица изделий
class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    sku = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    display_order = Column(Integer, default=0)
    album_id = Column(Integer, ForeignKey('albums.id'))
    is_available_to_order = Column(Boolean, default=True)
    is_visible = Column(Boolean, default=True)

    album = relationship("Album", back_populates="items")
    photos = relationship("Photo", back_populates="item")
    favorited_by = relationship("User", secondary=favorites_table, back_populates="favorites")
    cart_entries = relationship("Cart", back_populates="item")

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'sku': self.sku,
            'price': self.price,
            'display_order': self.display_order,
            'album_id': self.album_id,
            'is_available_to_order': self.is_available_to_order,
            'is_visible': self.is_visible
        }

# Таблица фотографий
class Photo(Base):
    __tablename__ = 'photos'
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    url = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    display_order = Column(Integer, default=0)

    item = relationship("Item", back_populates="photos")

    def to_dict(self):
        return {
            'id': self.id,
            'item_id': self.item_id,
            'url': self.url,
            'description': self.description,
            'display_order': self.display_order
        }

# Таблица администраторов
class AdminUser(Base):
    __tablename__ = 'admin_users'
    id = Column(Integer, primary_key=True)
    user_telegram_id = Column(Integer, unique=True, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_telegram_id': self.user_telegram_id
        }
