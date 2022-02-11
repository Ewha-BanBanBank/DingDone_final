package com.example.dingdone;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.ImageView;

public class AlarmActivity extends AppCompatActivity {
    ImageView siren;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_alarm);

        siren=(ImageView)findViewById(R.id.imageView2);
        siren.setOnClickListener(new MyListener());
        startService(new Intent(getApplicationContext(), MusicService.class));
    }

    @Override
    public void onDestroy() {
        stopService(new Intent(getApplicationContext(), MusicService.class));
        super.onDestroy();
    }

    @Override
    protected void onUserLeaveHint() {
        super.onUserLeaveHint();
        //이벤트 작성
        // System.exit(0);
        stopService(new Intent(getApplicationContext(), MusicService.class));
    }
    class MyListener implements View.OnClickListener{
        @Override
        public void onClick(View view){
            stopService(new Intent(getApplicationContext(), MusicService.class));
        }
    }
}