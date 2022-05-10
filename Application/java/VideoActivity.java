package com.example.dingdone;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.Toast;

import com.bumptech.glide.Glide;
import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.OnFailureListener;
import com.google.android.gms.tasks.OnSuccessListener;
import com.google.android.gms.tasks.Task;
import com.google.firebase.storage.FirebaseStorage;
import com.google.firebase.storage.ListResult;
import com.google.firebase.storage.StorageReference;


public class VideoActivity extends AppCompatActivity {
    Button buttonEvent1;
    Button buttonEvent2;

    FirebaseStorage storage = FirebaseStorage.getInstance();
    StorageReference listRef = storage.getReference().child("image_store");

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_video);

        listRef.listAll()
                .addOnSuccessListener(new OnSuccessListener<ListResult>() {
                    @Override
                    public void onSuccess(ListResult listResult) {
                        for (StorageReference item : listResult.getItems()) {
                            // ImageView 생성할 레이아웃 id 받아오기
                            LinearLayout layout=(LinearLayout) findViewById(R.id.imagesView);

                            // ImageView 동적 생성하기
                            ImageView iv=new ImageView(VideoActivity.this);
                            iv.setLayoutParams(new ViewGroup.LayoutParams(
                                    ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT));
                            layout.addView(iv);

                            // 사진 url 받아오기
                            item.getDownloadUrl().addOnCompleteListener(new OnCompleteListener<Uri>() {
                                @Override
                                public void onComplete(@NonNull Task<Uri> task) {
                                    if(task.isSuccessful()) {
                                        // Glide 이용해서 이미지뷰에 사진 띄우기
                                        Glide.with(VideoActivity.this).load(task.getResult()).into(iv);
                                    }
                                    else {
                                        // url 받아오지 못하면 토스트 메세지
                                        Toast.makeText(VideoActivity.this, task.getException().getMessage(), Toast.LENGTH_SHORT).show();
                                    }
                                }
                            });
                        }
                    }
                })
                .addOnFailureListener(new OnFailureListener() {
                    @Override
                    public void onFailure(@NonNull Exception e) {
                        // Uh-oh, an error occurred!
                    }
                });



        buttonEvent1 = (Button)findViewById(R.id.button1);
        buttonEvent1.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View view, MotionEvent motionEvent) {

                if(motionEvent.getAction() == MotionEvent.ACTION_DOWN) {
                    buttonEvent1.setBackgroundColor(Color.WHITE);
                    buttonEvent1.setTextColor(Color.BLACK);

                    Intent intent = new Intent(getApplicationContext(), MapActivity.class);
                    startActivity(intent);
                } else if(motionEvent.getAction() == MotionEvent.ACTION_UP) {
                    buttonEvent1.setBackgroundColor(Color.LTGRAY);
                }

                return false;
            }
        });

        buttonEvent2 = (Button)findViewById(R.id.button2);
        buttonEvent2.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View view, MotionEvent motionEvent) {

                if(motionEvent.getAction() == MotionEvent.ACTION_DOWN) {
                    buttonEvent2.setBackgroundColor(Color.WHITE);
                    buttonEvent2.setTextColor(Color.BLACK);
                } else if(motionEvent.getAction() == MotionEvent.ACTION_UP) {
                    buttonEvent2.setBackgroundColor(Color.WHITE);
                    buttonEvent2.setTextColor(Color.BLACK);
                }

                return false;
            }
        });
    }
}