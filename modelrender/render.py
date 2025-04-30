import os
import sys

# 1. Ваш улучшенный DOT-код (вставьте его сюда)
#    Убедитесь, что он заключен в тройные кавычки """ """.
dot_string = """
digraph model_graph {
    // Общие настройки графа
    graph [
        label = "Диаграмма моделей Django\nПроект: Lawyer Appointment System (Пример)", // Добавлен заголовок
        labelloc = "t", // Расположение заголовка сверху
        fontname = "Roboto, Arial, sans-serif", // Добавлены запасные шрифты
        fontsize = 12, // Увеличен размер шрифта заголовка
        rankdir = TB, // Направление сверху вниз
        splines = true, // Использовать сглаженные линии (можно заменить на 'ortho' для прямых углов)
        concentrate = true, // Объединять параллельные ребра
        nodesep = 0.6, // Расстояние между узлами на одном уровне
        ranksep = 0.8, // Расстояние между уровнями
        bgcolor = "#f8f9fa" // Легкий фон для графа
        // bb="0,0,954.38,899.26", // Убрано, Graphviz вычислит сам
    ];

    // Общие настройки узлов (моделей)
    node [
        fontname = "Roboto, Arial, sans-serif",
        fontsize = 9, // Немного увеличен базовый размер шрифта
        shape = plaintext // Форма узла определяется HTML-лейблом
    ];

    // Общие настройки ребер (связей)
    edge [
        fontname = "Roboto, Arial, sans-serif",
        fontsize = 8,
        arrowsize = 0.8 // Немного уменьшен размер стрелок
    ];

    // Определения узлов (моделей) с улучшенными HTML-лейблами

    // --- django.contrib.auth ---
    subgraph cluster_auth {
        label = "django.contrib.auth";
        style = "filled";
        color = "#e9f5ee"; // Светло-зеленый фон для группы
        node [ node_color = "#1b563f" ]; // Цвет заголовка для этой группы

        django_contrib_auth_models_AbstractUser [
            label = <
                <TABLE BGCOLOR="white" BORDER="1" CELLBORDER="0" CELLSPACING="0" STYLE="rounded">
                <TR><TD COLSPAN="2" CELLPADDING="5" ALIGN="CENTER" BGCOLOR="#1b563f">
                <FONT FACE="Roboto, Arial, sans-serif" COLOR="white" POINT-SIZE="10"><B>AbstractUser</B></FONT><BR/>
                <FONT FACE="Roboto, Arial, sans-serif" COLOR="#dddddd" POINT-SIZE="8">(django.contrib.auth)<BR/><I>Наследует: AbstractBaseUser, PermissionsMixin</I></FONT>
                </TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif">date_joined</FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif">DateTimeField</FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT COLOR="#7B7B7B" FACE="Roboto, Arial, sans-serif">email</FONT></TD><TD ALIGN="LEFT"><FONT COLOR="#7B7B7B" FACE="Roboto, Arial, sans-serif">EmailField</FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT COLOR="#7B7B7B" FACE="Roboto, Arial, sans-serif">first_name</FONT></TD><TD ALIGN="LEFT"><FONT COLOR="#7B7B7B" FACE="Roboto, Arial, sans-serif">CharField</FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif">is_active</FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif">BooleanField</FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif">is_staff</FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif">BooleanField</FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif"><I>is_superuser</I></FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif"><I>BooleanField</I></FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT COLOR="#7B7B7B" FACE="Roboto, Arial, sans-serif"><I>last_login</I></FONT></TD><TD ALIGN="LEFT"><FONT COLOR="#7B7B7B" FACE="Roboto, Arial, sans-serif"><I>DateTimeField</I></FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT COLOR="#7B7B7B" FACE="Roboto, Arial, sans-serif">last_name</FONT></TD><TD ALIGN="LEFT"><FONT COLOR="#7B7B7B" FACE="Roboto, Arial, sans-serif">CharField</FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif"><I>password</I></FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif"><I>CharField</I></FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif">username</FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif">CharField</FONT></TD></TR>
                </TABLE>
            >
        ];

        django_contrib_auth_base_user_AbstractBaseUser [
            label = <
              <TABLE BGCOLOR="white" BORDER="0" CELLBORDER="0" CELLSPACING="0" STYLE="rounded">
              <TR><TD COLSPAN="2" CELLPADDING="4" ALIGN="CENTER" BGCOLOR="#1b563f">
              <FONT FACE="Roboto, Arial, sans-serif" POINT-SIZE="10" COLOR="white"><B>AbstractBaseUser</B></FONT><BR/>
              <FONT FACE="Roboto, Arial, sans-serif" POINT-SIZE="8" COLOR="#dddddd">(django.contrib.auth.base_user)</FONT>
              </TD></TR>
              </TABLE>
            >
        ];

        django_contrib_auth_models_PermissionsMixin [
            label = <
              <TABLE BGCOLOR="white" BORDER="0" CELLBORDER="0" CELLSPACING="0" STYLE="rounded">
              <TR><TD COLSPAN="2" CELLPADDING="4" ALIGN="CENTER" BGCOLOR="#1b563f">
              <FONT FACE="Roboto, Arial, sans-serif" POINT-SIZE="10" COLOR="white"><B>PermissionsMixin</B></FONT><BR/>
               <FONT FACE="Roboto, Arial, sans-serif" POINT-SIZE="8" COLOR="#dddddd">(django.contrib.auth.models)</FONT>
              </TD></TR>
              </TABLE>
            >
        ];

        django_contrib_auth_models_Permission [
            label = <
                <TABLE BGCOLOR="white" BORDER="1" CELLBORDER="0" CELLSPACING="0" STYLE="rounded">
                <TR><TD COLSPAN="2" CELLPADDING="5" ALIGN="CENTER" BGCOLOR="#1b563f">
                <FONT FACE="Roboto, Arial, sans-serif" COLOR="white" POINT-SIZE="10"><B>Permission</B></FONT><BR/>
                <FONT FACE="Roboto, Arial, sans-serif" COLOR="#dddddd" POINT-SIZE="8">(django.contrib.auth)</FONT>
                </TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif"><B>id</B></FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif"><B>AutoField</B></FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif"><B>content_type</B></FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif"><B>ForeignKey (ContentType)</B></FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif">codename</FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif">CharField</FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif">name</FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif">CharField</FONT></TD></TR>
                </TABLE>
            >
        ];

        django_contrib_auth_models_Group [
            label = <
                <TABLE BGCOLOR="white" BORDER="1" CELLBORDER="0" CELLSPACING="0" STYLE="rounded">
                <TR><TD COLSPAN="2" CELLPADDING="5" ALIGN="CENTER" BGCOLOR="#1b563f">
                <FONT FACE="Roboto, Arial, sans-serif" COLOR="white" POINT-SIZE="10"><B>Group</B></FONT><BR/>
                <FONT FACE="Roboto, Arial, sans-serif" COLOR="#dddddd" POINT-SIZE="8">(django.contrib.auth)</FONT>
                </TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif"><B>id</B></FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif"><B>AutoField</B></FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif">name</FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif">CharField</FONT></TD></TR>
                </TABLE>
            >
        ];
    }

    // --- django.contrib.contenttypes ---
     subgraph cluster_contenttypes {
        label = "django.contrib.contenttypes";
        style = "filled";
        color = "#e3f2fd"; // Светло-голубой фон для группы
        node [ node_color = "#0277bd" ]; // Цвет заголовка для этой группы

        django_contrib_contenttypes_models_ContentType [
            label = <
                <TABLE BGCOLOR="white" BORDER="1" CELLBORDER="0" CELLSPACING="0" STYLE="rounded">
                <TR><TD COLSPAN="2" CELLPADDING="5" ALIGN="CENTER" BGCOLOR="#0277bd">
                <FONT FACE="Roboto, Arial, sans-serif" COLOR="white" POINT-SIZE="10"><B>ContentType</B></FONT><BR/>
                <FONT FACE="Roboto, Arial, sans-serif" COLOR="#dddddd" POINT-SIZE="8">(django.contrib.contenttypes)</FONT>
                </TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif"><B>id</B></FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif"><B>AutoField</B></FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif">app_label</FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif">CharField</FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif">model</FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif">CharField</FONT></TD></TR>
                </TABLE>
            >
        ];
    }

    // --- django.contrib.admin ---
    subgraph cluster_admin {
        label = "django.contrib.admin";
        style = "filled";
        color = "#f8f9fa"; // Светло-серый фон
        node [ node_color = "#6c757d" ]; // Цвет заголовка

        django_contrib_admin_models_LogEntry [
            label = <
                <TABLE BGCOLOR="white" BORDER="1" CELLBORDER="0" CELLSPACING="0" STYLE="rounded">
                <TR><TD COLSPAN="2" CELLPADDING="5" ALIGN="CENTER" BGCOLOR="#6c757d">
                <FONT FACE="Roboto, Arial, sans-serif" COLOR="white" POINT-SIZE="10"><B>LogEntry</B></FONT><BR/>
                <FONT FACE="Roboto, Arial, sans-serif" COLOR="#dddddd" POINT-SIZE="8">(django.contrib.admin)</FONT>
                </TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif"><B>id</B></FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif"><B>AutoField</B></FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT COLOR="#7B7B7B" FACE="Roboto, Arial, sans-serif"><B>content_type</B></FONT></TD><TD ALIGN="LEFT"><FONT COLOR="#7B7B7B" FACE="Roboto, Arial, sans-serif"><B>ForeignKey (ContentType)</B></FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif"><B>user</B></FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif"><B>ForeignKey (User)</B></FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif">action_flag</FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif">PositiveSmallIntegerField</FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif">action_time</FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif">DateTimeField</FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT COLOR="#7B7B7B" FACE="Roboto, Arial, sans-serif">change_message</FONT></TD><TD ALIGN="LEFT"><FONT COLOR="#7B7B7B" FACE="Roboto, Arial, sans-serif">TextField</FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT COLOR="#7B7B7B" FACE="Roboto, Arial, sans-serif">object_id</FONT></TD><TD ALIGN="LEFT"><FONT COLOR="#7B7B7B" FACE="Roboto, Arial, sans-serif">TextField</FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif">object_repr</FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif">CharField</FONT></TD></TR>
                </TABLE>
            >
        ];
    }

    // --- django.contrib.sessions ---
    subgraph cluster_sessions {
        label = "django.contrib.sessions";
        style = "filled";
        color = "#e0f2f7"; // Очень светло-голубой
        node [ node_color = "#00796b" ]; // Цвет заголовка

        django_contrib_sessions_base_session_AbstractBaseSession [
            label = <
                <TABLE BGCOLOR="white" BORDER="1" CELLBORDER="0" CELLSPACING="0" STYLE="rounded">
                <TR><TD COLSPAN="2" CELLPADDING="5" ALIGN="CENTER" BGCOLOR="#00796b">
                <FONT FACE="Roboto, Arial, sans-serif" COLOR="white" POINT-SIZE="10"><B>AbstractBaseSession</B></FONT><BR/>
                <FONT FACE="Roboto, Arial, sans-serif" COLOR="#dddddd" POINT-SIZE="8">(django.contrib.sessions.base_session)</FONT>
                </TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif">expire_date</FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif">DateTimeField</FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif">session_data</FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif">TextField</FONT></TD></TR>
                </TABLE>
            >
        ];

        django_contrib_sessions_models_Session [
            label = <
                <TABLE BGCOLOR="white" BORDER="1" CELLBORDER="0" CELLSPACING="0" STYLE="rounded">
                <TR><TD COLSPAN="2" CELLPADDING="5" ALIGN="CENTER" BGCOLOR="#00796b">
                <FONT FACE="Roboto, Arial, sans-serif" COLOR="white" POINT-SIZE="10"><B>Session</B></FONT><BR/>
                <FONT FACE="Roboto, Arial, sans-serif" COLOR="#dddddd" POINT-SIZE="8">(django.contrib.sessions)<BR/><I>Наследует: AbstractBaseSession</I></FONT>
                </TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif"><I><B>session_key</B></I></FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif"><I><B>CharField (Primary Key)</B></I></FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif"><I>expire_date</I></FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif"><I>DateTimeField</I></FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif"><I>session_data</I></FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif"><I>TextField</I></FONT></TD></TR>
                </TABLE>
            >
        ];
    }

    // --- Приложение: accounts ---
    subgraph cluster_accounts {
        label = "Приложение: accounts";
        style = "filled";
        color = "#e6e6fa"; // Светло-лавандовый
        node [ node_color = "#4682b4" ]; // Стальной синий

        accounts_models_CustomUser [
            label = <
                <TABLE BGCOLOR="white" BORDER="1" CELLBORDER="0" CELLSPACING="0" STYLE="rounded">
                <TR><TD COLSPAN="2" CELLPADDING="5" ALIGN="CENTER" BGCOLOR="#4682b4">
                <FONT FACE="Roboto, Arial, sans-serif" COLOR="white" POINT-SIZE="10"><B>CustomUser</B> (Пользователь)</FONT><BR/>
                <FONT FACE="Roboto, Arial, sans-serif" COLOR="#dddddd" POINT-SIZE="8">(accounts)<BR/><I>Наследует: AbstractUser</I></FONT>
                </TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif"><B>id</B></FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif"><B>BigAutoField</B></FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif"><I>date_joined</I></FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif"><I>DateTimeField</I></FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif">email</FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif">EmailField</FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT COLOR="#7B7B7B" FACE="Roboto, Arial, sans-serif"><I>first_name</I></FONT></TD><TD ALIGN="LEFT"><FONT COLOR="#7B7B7B" FACE="Roboto, Arial, sans-serif"><I>CharField</I></FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif">full_name</FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif">CharField</FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif"><I>is_active</I></FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif"><I>BooleanField</I></FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif"><I>is_staff</I></FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif"><I>BooleanField</I></FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif"><I>is_superuser</I></FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif"><I>BooleanField</I></FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT COLOR="#7B7B7B" FACE="Roboto, Arial, sans-serif"><I>last_login</I></FONT></TD><TD ALIGN="LEFT"><FONT COLOR="#7B7B7B" FACE="Roboto, Arial, sans-serif"><I>DateTimeField</I></FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT COLOR="#7B7B7B" FACE="Roboto, Arial, sans-serif"><I>last_name</I></FONT></TD><TD ALIGN="LEFT"><FONT COLOR="#7B7B7B" FACE="Roboto, Arial, sans-serif"><I>CharField</I></FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif"><I>password</I></FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif"><I>CharField</I></FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif">phone</FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif">CharField</FONT></TD></TR>
                </TABLE>
            >
        ];

        accounts_models_LawyerProfile [
            label = <
                <TABLE BGCOLOR="white" BORDER="1" CELLBORDER="0" CELLSPACING="0" STYLE="rounded">
                <TR><TD COLSPAN="2" CELLPADDING="5" ALIGN="CENTER" BGCOLOR="#4682b4">
                <FONT FACE="Roboto, Arial, sans-serif" COLOR="white" POINT-SIZE="10"><B>LawyerProfile</B> (Профиль Юриста)</FONT><BR/>
                <FONT FACE="Roboto, Arial, sans-serif" COLOR="#dddddd" POINT-SIZE="8">(accounts)</FONT>
                </TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif"><B>id</B></FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif"><B>BigAutoField</B></FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif"><B>user</B></FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif"><B>OneToOneField (CustomUser)</B></FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif">office_address</FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif">CharField</FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif">specialization</FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif">CharField</FONT></TD></TR>
                </TABLE>
            >
        ];
    }

    // --- Приложение: appointments ---
    subgraph cluster_appointments {
        label = "Приложение: appointments";
        style = "filled";
        color = "#f3e5f5"; // Светло-фиолетовый
        node [ node_color = "#8e24aa" ]; // Фиолетовый

        appointments_models_Appointment [
            label = <
                <TABLE BGCOLOR="white" BORDER="1" CELLBORDER="0" CELLSPACING="0" STYLE="rounded">
                <TR><TD COLSPAN="2" CELLPADDING="5" ALIGN="CENTER" BGCOLOR="#8e24aa">
                <FONT FACE="Roboto, Arial, sans-serif" COLOR="white" POINT-SIZE="10"><B>Appointment</B> (Запись на приём)</FONT><BR/>
                <FONT FACE="Roboto, Arial, sans-serif" COLOR="#dddddd" POINT-SIZE="8">(appointments)</FONT>
                </TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif"><B>id</B></FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif"><B>BigAutoField</B></FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif"><B>client</B></FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif"><B>ForeignKey (CustomUser)</B></FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif"><B>lawyer</B></FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif"><B>ForeignKey (CustomUser)</B></FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT COLOR="#7B7B7B" FACE="Roboto, Arial, sans-serif">created_at</FONT></TD><TD ALIGN="LEFT"><FONT COLOR="#7B7B7B" FACE="Roboto, Arial, sans-serif">DateTimeField</FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif">date</FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif">DateTimeField</FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif">status</FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif">CharField</FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT COLOR="#7B7B7B" FACE="Roboto, Arial, sans-serif">updated_at</FONT></TD><TD ALIGN="LEFT"><FONT COLOR="#7B7B7B" FACE="Roboto, Arial, sans-serif">DateTimeField</FONT></TD></TR>
                </TABLE>
            >
        ];

        appointments_models_CalendarSlot [
            label = <
                <TABLE BGCOLOR="white" BORDER="1" CELLBORDER="0" CELLSPACING="0" STYLE="rounded">
                <TR><TD COLSPAN="2" CELLPADDING="5" ALIGN="CENTER" BGCOLOR="#8e24aa">
                <FONT FACE="Roboto, Arial, sans-serif" COLOR="white" POINT-SIZE="10"><B>CalendarSlot</B> (Слот в календаре)</FONT><BR/>
                <FONT FACE="Roboto, Arial, sans-serif" COLOR="#dddddd" POINT-SIZE="8">(appointments)</FONT>
                </TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif"><B>id</B></FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif"><B>BigAutoField</B></FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif"><B>lawyer</B></FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif"><B>ForeignKey (CustomUser)</B></FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT COLOR="#7B7B7B" FACE="Roboto, Arial, sans-serif">created_at</FONT></TD><TD ALIGN="LEFT"><FONT COLOR="#7B7B7B" FACE="Roboto, Arial, sans-serif">DateTimeField</FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif">end_time</FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif">DateTimeField</FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif">is_booked</FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif">BooleanField</FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT FACE="Roboto, Arial, sans-serif">start_time</FONT></TD><TD ALIGN="LEFT"><FONT FACE="Roboto, Arial, sans-serif">DateTimeField</FONT></TD></TR>
                <TR><TD ALIGN="LEFT" BORDER="0"><FONT COLOR="#7B7B7B" FACE="Roboto, Arial, sans-serif">updated_at</FONT></TD><TD ALIGN="LEFT"><FONT COLOR="#7B7B7B" FACE="Roboto, Arial, sans-serif">DateTimeField</FONT></TD></TR>
                </TABLE>
            >
        ];
    }


    // Определения ребер (связей)

    // --- Наследование ---
    django_contrib_auth_models_AbstractUser -> django_contrib_auth_base_user_AbstractBaseUser [
        arrowhead = empty, tailclip = false, dir = both, style=dashed, color="#555555",
        label = " абстрактное\n наследование"
    ];
    django_contrib_auth_models_AbstractUser -> django_contrib_auth_models_PermissionsMixin [
        arrowhead = empty, tailclip = false, dir = both, style=dashed, color="#555555",
        label = " абстрактное\n наследование"
    ];
    accounts_models_CustomUser -> django_contrib_auth_models_AbstractUser [
        arrowhead = empty, tailclip = false, dir = both, style=dashed, color="#555555",
        label = " абстрактное\n наследование"
    ];
     django_contrib_sessions_models_Session -> django_contrib_sessions_base_session_AbstractBaseSession [
        arrowhead = empty, tailclip = false, dir = both, style=dashed, color="#555555",
        label = " абстрактное\n наследование"
    ];

    // --- Связи ForeignKey ---
    django_contrib_auth_models_Permission -> django_contrib_contenttypes_models_ContentType [
        arrowhead = none, arrowtail = crow, dir = both, color="#0277bd", // Цвет связи ContentType
        label = " content_type"
    ];
    django_contrib_admin_models_LogEntry -> django_contrib_contenttypes_models_ContentType [
        arrowhead = none, arrowtail = crow, dir = both, color="#0277bd",
        label = " content_type", constraint=false // constraint=false может помочь с пересечениями
    ];
    django_contrib_admin_models_LogEntry -> accounts_models_CustomUser [
        arrowhead = none, arrowtail = crow, dir = both, color="#4682b4", // Цвет связи User
        label = " user"
    ];
    appointments_models_Appointment -> accounts_models_CustomUser [
        arrowhead = none, arrowtail = crow, dir = both, color="#4682b4",
        label = " client\n(клиент)"
    ];
    appointments_models_Appointment -> accounts_models_CustomUser [
        arrowhead = none, arrowtail = crow, dir = both, color="#4682b4",
        label = " lawyer\n(юрист)"
    ];
     appointments_models_CalendarSlot -> accounts_models_CustomUser [
        arrowhead = none, arrowtail = crow, dir = both, color="#4682b4",
        label = " lawyer\n(юрист)"
    ];

    // --- Связи ManyToMany ---
    accounts_models_CustomUser -> django_contrib_auth_models_Permission [
        arrowhead = crow, arrowtail = crow, dir = both, color="#1b563f", // Цвет связи Auth
        label = " user_permissions"
    ];
    accounts_models_CustomUser -> django_contrib_auth_models_Group [
        arrowhead = crow, arrowtail = crow, dir = both, color="#1b563f",
        label = " groups"
    ];
    django_contrib_auth_models_Group -> django_contrib_auth_models_Permission [
        arrowhead = crow, arrowtail = crow, dir = both, color="#1b563f",
        label = " permissions"
    ];

    // --- Связи OneToOne ---
    accounts_models_LawyerProfile -> accounts_models_CustomUser [
        arrowhead = none, arrowtail = icurve, dir = both, color="#4682b4", // icurve для OneToOne
        label = " user\n(1-к-1)"
    ];

    // Указание рангов для лучшего вертикального выравнивания (опционально)
    { rank=min; django_contrib_auth_base_user_AbstractBaseUser; django_contrib_auth_models_PermissionsMixin; django_contrib_contenttypes_models_ContentType; }
    { rank=same; django_contrib_auth_models_AbstractUser; django_contrib_auth_models_Group; django_contrib_auth_models_Permission; django_contrib_sessions_base_session_AbstractBaseSession; }
    { rank=same; accounts_models_CustomUser; }
    { rank=max; accounts_models_LawyerProfile; django_contrib_admin_models_LogEntry; appointments_models_Appointment; appointments_models_CalendarSlot; django_contrib_sessions_models_Session; }
}
"""

# 2. Настройки рендеринга
output_filename = "model_diagram_rendered.png"  # Имя выходного файла
output_format = "png"  # Формат ('png', 'svg', 'pdf', 'jpg', etc.)
layout_engine = "dot"  # Движок компоновки ('dot', 'neato', 'fdp', 'sfdp', 'twopi', 'circo')
                        # 'dot' - лучший для иерархических графов (как этот)

# 3. Функция рендеринга
def render_graph(dot_code, filename, format, engine):
    """
    Рендерит граф из DOT-строки в файл с использованием pygraphviz.

    Args:
        dot_code (str): Строка с описанием графа в формате DOT.
        filename (str): Путь к выходному файлу.
        format (str): Формат выходного файла (например, 'png', 'svg').
        engine (str): Движок компоновки Graphviz (например, 'dot', 'neato').
    """
    print(f"Попытка рендеринга графа в '{filename}' (формат: {format}, движок: {engine})...")
    try:
        # Создаем граф из строки
        # strict=False важен для работы с кластерами и потенциально сложными графами
        # directed=True, так как исходный граф - digraph
        G = pgv.AGraph(string=dot_code, strict=False, directed=True)

        # Устанавливаем движок компоновки
        G.graph_attr['rankdir'] = 'TB' # Убедимся, что rankdir применяется
        G.layout(prog=engine)

        # Рендерим граф в файл
        G.draw(filename, format=format)

        print(f"Граф успешно сохранен в '{os.path.abspath(filename)}'")

    except ImportError:
        print("Ошибка: Библиотека pygraphviz не найдена.", file=sys.stderr)
        print("Пожалуйста, установите ее: pip install pygraphviz", file=sys.stderr)
        # На Windows может потребоваться установка из неофициальных бинарников:
        # https://www.lfd.uci.edu/~gohlke/pythonlibs/#pygraphviz
        # Также убедитесь, что сама программа Graphviz установлена и добавлена в PATH.
    except Exception as e:
        print(f"Ошибка во время рендеринга графа: {e}", file=sys.stderr)
        print("Убедитесь, что Graphviz установлен и доступен в системном PATH.", file=sys.stderr)
        print("Проверьте корректность DOT-синтаксиса.", file=sys.stderr)

# 4. Запуск рендеринга
if __name__ == "__main__":
    render_graph(dot_string, output_filename, output_format, layout_engine)

    # --- Пример рендеринга в SVG ---
    # svg_filename = "model_diagram_rendered.svg"
    # render_graph(dot_string, svg_filename, "svg", layout_engine)
    # print("\nТакже сгенерирован SVG файл.")