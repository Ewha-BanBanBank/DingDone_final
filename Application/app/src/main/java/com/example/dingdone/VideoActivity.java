package com.example.dingdone;

import androidx.appcompat.app.AppCompatActivity;

import android.graphics.Color;
import android.os.Bundle;
import android.view.MotionEvent;
import android.view.View;
import android.widget.Button;

public class VideoActivity extends AppCompatActivity {
    Button buttonEvent1;
    Button buttonEvent2;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_video);

        buttonEvent1 = (Button)findViewById(R.id.button1);
        buttonEvent1.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View view, MotionEvent motionEvent) {

                if(motionEvent.getAction() == MotionEvent.ACTION_DOWN) {
                    buttonEvent1.setBackgroundColor(Color.WHITE);
                    buttonEvent1.setTextColor(Color.BLACK);
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